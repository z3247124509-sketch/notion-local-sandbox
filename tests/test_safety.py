"""Standard-library tests; no Docker, network, credentials or third-party imports."""
import asyncio
import hashlib
import io
import json
import os
import signal
import socket
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest.mock import patch
from email.message import Message

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import launch
from auth import Auth, bearer_digest
from gateway import configuration
from origin_proxy import Handler
import origin_proxy
from safe_files import Denied, Store, MAX_TEXT, parts
import server

# Public test fixture, deliberately not random and never used by the launcher.
FIXTURE_TOKEN = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"


class Files(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "samples").mkdir()
        (self.root / "notes").mkdir()
        self.store = Store(self.root)

    def test_roundtrip_and_compare_replace(self):
        self.store.write("notes/test.txt", "before")
        with self.assertRaises(Denied):
            self.store.write("notes/test.txt", "wrong", "stale")
        self.store.write("notes/test.txt", "after", "before")
        self.assertEqual(self.store.read("notes/test.txt"), "after")
        with self.assertRaises(FileExistsError):
            self.store.write("notes/test.txt", "overwrite")

    def test_traversal_and_hidden_paths(self):
        for p in ["/etc/passwd", "../a.txt", "notes/../a.txt", "notes/.env", "notes//a.txt",
                  "notes/./a.txt", "samples/nested/a.txt", "notes\\a.txt", "notes/a.py", "notes/a\n.txt"]:
            with self.subTest(path=p), self.assertRaises(Denied):
                parts(p)

    def test_symlinks_and_hardlinks(self):
        outside = self.root / "outside.txt"
        outside.write_text("synthetic outside marker")
        (self.root / "notes/link.txt").symlink_to(outside)
        os.link(outside, self.root / "notes/hard.txt")
        for p in ["notes/link.txt", "notes/hard.txt"]:
            with self.subTest(path=p), self.assertRaises((Denied, OSError)):
                self.store.read(p)
        self.assertEqual(self.store.list(), [])

    def test_parent_directory_symlink(self):
        (self.root / "notes").rmdir()
        (self.root / "notes").symlink_to(self.root / "samples")
        with self.assertRaises(OSError):
            self.store.write("notes/a.txt", "denied")

    def test_fifo_does_not_block(self):
        os.mkfifo(self.root / "notes/pipe.txt")
        with self.assertRaises(Denied):
            self.store.read("notes/pipe.txt")

    def test_limits(self):
        for value in ["a" * (MAX_TEXT + 1), "x\x00y", "界" * MAX_TEXT]:
            with self.assertRaises(Denied):
                self.store.write("notes/large.txt", value)
        for n in range(100):
            self.store.write("notes/" + str(n) + ".txt", "x")
        with self.assertRaises(Denied):
            self.store.write("notes/extra.txt", "x")

    def test_json_check(self):
        self.store.write("samples/example.json", '{"message":"sample","count":1}')
        self.assertTrue(self.store.check_json()["passed"])
        self.store.write("samples/example.json", '{"message":"sample","count":true}',
                         self.store.read("samples/example.json"))
        with self.assertRaises(Denied):
            self.store.check_json()


class Authentication(unittest.IsolatedAsyncioTestCase):
    async def request(self, headers=None, body=b"{}", path="/mcp", query=b"", method="POST"):
        output = []
        reached = []
        async def app(scope, receive, send):
            reached.append((await receive())["body"])
            await send({"type": "http.response.start", "status": 200})
        async def receive():
            return {"type": "http.request", "body": body}
        async def send(event):
            output.append(event)
        scope = {"type": "http", "headers": headers if headers is not None else
                 [(b"authorization", b"Bearer " + FIXTURE_TOKEN.encode())],
                 "path": path, "query_string": query, "method": method}
        await Auth(app, bearer_digest(FIXTURE_TOKEN))(scope, receive, send)
        return output[0]["status"], reached

    async def test_valid(self):
        self.assertEqual(await self.request(), (200, [b"{}"]))

    async def test_missing_invalid_and_duplicate(self):
        good = (b"authorization", b"Bearer " + FIXTURE_TOKEN.encode())
        for headers in [[], [(b"authorization", b"Bearer wrong")], [good, good],
                        [(b"authorization", b"Bearer " + FIXTURE_TOKEN[::-1].encode())]]:
            self.assertEqual(await self.request(headers=headers), (401, []))

    async def test_route_and_body_limits(self):
        self.assertEqual(await self.request(path="/"), (404, []))
        self.assertEqual(await self.request(query=b"token=never-accept-query-tokens"), (404, []))
        self.assertEqual(await self.request(method="PUT"), (405, []))
        self.assertEqual(await self.request(body=b"x" * 65537), (413, []))


class Tools(unittest.TestCase):
    def test_inert_tunnels_do_not_relax_offline_policy(self):
        server.validate_network({'lo':(9,'unknown'),'tunl0':(0,'down')},[],[],0,1)
        bad = [({'lo':(9,'unknown'),'eth0':(0,'down')},[],[],0,1),
               ({'lo':(9,'unknown'),'tunl0':(1,'up')},[],[],0,1),
               ({'lo':(9,'unknown')},['external route'],[],0,1),
               ({'lo':(9,'unknown')},[],['route eth0'],0,1),
               ({'lo':(9,'unknown')},[],[],1,1),
               ({'lo':(9,'unknown')},[],[],0,0)]
        for args in bad:
            with self.assertRaises(RuntimeError):server.validate_network(*args)

    def test_only_fixed_tools_no_general_execution(self):
        class FakeMCP:
            def __init__(self, *args): self.tools = {}
            def tool(self, fn): self.tools[fn.__name__] = fn; return fn
        with patch.dict(sys.modules, {"fastmcp": types.SimpleNamespace(FastMCP=FakeMCP)}):
            app = server.create_server()
        self.assertEqual(set(app.tools), {"list_files", "read_file", "write_file", "run_check"})
        with patch.object(server.subprocess, "run") as execute:
            for name in ["sh", "echo safe; touch anything", "codex", "claude", "../self_test"]:
                self.assertEqual(app.tools["run_check"](name), {"error": "check_not_allowed"})
            execute.assert_not_called()


class Launch(unittest.TestCase):
    def test_ordinary_exit_signals_enter_cleanup(self):
        with patch.object(launch.signal, "signal") as register:
            launch.install_exit_handlers()
        self.assertEqual({call.args[0] for call in register.call_args_list}, {signal.SIGTERM, signal.SIGHUP})
        for call in register.call_args_list:
            with self.assertRaises(KeyboardInterrupt):
                call.args[1](call.args[0], None)

    def test_failed_stop_still_attempts_other_container(self):
        class FakeDocker:
            def __init__(self): self.attempts = []
            def owns(self, kind, name, session): return True
            def call(self, args):
                self.attempts.append(args)
                if args[:2] == ["container", "rm"] and args[-1] == "gateway":
                    raise RuntimeError("synthetic stop failure")
                return types.SimpleNamespace(stdout="")
        docker = FakeDocker()
        with self.assertRaises(RuntimeError):
            launch.stop(docker, {"session": "synthetic", "containers": ["control", "gateway"]})
        self.assertIn(["container", "rm", "--force", "control"], docker.attempts)

    def test_container_boundaries(self):
        image = "sha256:" + "a" * 64
        for data in ["synthetic-data", None]:
            args = launch.run_args("container", "id", image, "ipc", data)
            self.assertIn("--pull=never", args)
            self.assertIn("--read-only", args)
            self.assertIn("--user=10001:10001", args)
            self.assertNotIn("-p", args)
            self.assertNotIn("--privileged", args)
            self.assertNotIn("type=bind", " ".join(args))
            self.assertNotIn("docker.sock", " ".join(args))
            self.assertIn("--network=none" if data else "--network=bridge", args)
            if not data:
                self.assertNotIn("dst=/workspace", " ".join(args))
                self.assertIn("readonly,volume-nocopy", " ".join(args))

    def test_unpinned_images_denied(self):
        for image in ["latest", "python:3.12", "sha256:" + "x" * 64]:
            with self.assertRaises(ValueError):
                launch.image_id(image)

    def test_hidden_input_required(self):
        with patch.object(sys.stdin, "isatty", return_value=False):
            with self.assertRaises(ValueError):
                launch.secret("Test: ")

    def test_existing_docker_credentials_not_used(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            config = runtime / "empty-docker-config"
            config.mkdir()
            (config / "config.json").write_text('{"synthetic":"never-read"}')
            with self.assertRaises(ValueError):
                launch.Docker("/usr/local/bin/docker", "unix:///synthetic.sock", runtime)

    def test_scope_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "state.json"
            p.write_text(json.dumps({"session": "a" * 32, "containers": ["unrelated"], "volumes": []}))
            with self.assertRaises(ValueError):
                launch.load_state(p)


class Gateway(unittest.TestCase):
    def test_absolute_deadline_includes_headers_and_body(self):
        for request in [b"POST /mcp HTTP/1.1\r\nHost: incomplete",
                        b"POST /mcp HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer PUBLIC_TEST_VALUE\r\nContent-Length: 100\r\n\r\nx"]:
            client, worker = socket.socketpair()
            self.addCleanup(client.close)
            self.addCleanup(worker.close)
            def handle():
                try:
                    Handler(worker, ("local", 0), types.SimpleNamespace())
                except (OSError, ValueError):
                    pass
            with patch.object(origin_proxy, "REQUEST_DEADLINE_SECONDS", 0.05):
                thread = threading.Thread(target=handle, daemon=True)
                thread.start()
                client.sendall(request)
                # Keep making progress; a per-read idle timeout would not help.
                for _ in range(4):
                    time.sleep(0.02)
                    try:
                        client.sendall(b"x")
                    except OSError:
                        break
                thread.join(timeout=0.5)
                self.assertFalse(thread.is_alive(), "Absolute request deadline failed")

    def test_config_secret_is_only_in_volatile_config(self):
        domain, config = configuration({"domain": "synthetic-demo.ngrok-free.app", "authtoken": "PUBLIC_TEST_VALUE"})
        self.assertEqual(config["agent"]["authtoken"], "PUBLIC_TEST_VALUE")
        for key in ["web_addr", "remote_management", "update_check"]:
            self.assertFalse(config["agent"][key])

    def test_domains_and_tokens(self):
        for domain in ["localhost", "example.com", "bad.ngrok-free.app/anything"]:
            with self.assertRaises(ValueError):
                configuration({"domain": domain, "authtoken": "PUBLIC_TEST_VALUE"})
        with self.assertRaises(ValueError):
            configuration({"domain": "synthetic-demo.ngrok-free.app", "authtoken": "bad\nvalue"})

    def body(self, headers, body):
        handler = Handler.__new__(Handler)
        handler.headers = Message()
        for k, v in headers:
            handler.headers[k] = v
        handler.rfile = io.BytesIO(body)
        return handler.body()

    def test_chunked_body(self):
        self.assertEqual(self.body([("Transfer-Encoding", "chunked")], b"2\r\n{}\r\n0\r\n\r\n"), b"{}")

    def test_ambiguous_and_oversized_bodies(self):
        for headers, body in [([("Content-Length", "2"), ("Transfer-Encoding", "chunked")], b"{}"),
                              ([("Content-Length", "2"), ("Content-Length", "2")], b"{}"),
                              ([("Content-Length", "65537")], b""),
                              ([("Transfer-Encoding", "chunked")], b"0\r\nAuthorization: hidden\r\n")]:
            with self.assertRaises((ValueError, OverflowError)):
                self.body(headers, body)


if __name__ == "__main__":
    unittest.main()
