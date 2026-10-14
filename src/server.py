"""Container-only MCP entry point, exposing synthetic text and fixed checks."""
import asyncio
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auth import Auth
from safe_files import Store


def validate_network(links, ipv4_rows, ipv6_rows, effective_caps, no_new_privileges):
    dormant = {"tunl0", "gre0", "gretap0", "erspan0", "ip_vti0", "ip6_vti0", "sit0", "ip6tnl0", "ip6gre0"}
    if "lo" not in links or set(links) - {"lo"} - dormant:
        raise RuntimeError("Unexpected interface in offline namespace")
    for name, (flags, state) in links.items():
        if name == "lo":
            if flags & 9 != 9:
                raise RuntimeError("Loopback is not up")
        elif flags & 1 or state != "down":
            raise RuntimeError("Non-loopback interface is active")
    if ipv4_rows or any(row.split()[-1] != "lo" for row in ipv6_rows if row.strip()):
        raise RuntimeError("External route in offline namespace")
    if effective_caps != 0 or no_new_privileges != 1:
        raise RuntimeError("Privileges exceed offline policy")


def verify_runtime():
    if os.geteuid() != 10001 or not Path("/.dockerenv").is_file():
        raise RuntimeError("Non-root Linux container required")
    if not os.statvfs("/opt/kit").f_flag & os.ST_RDONLY:
        raise RuntimeError("Read-only root required")
    # Some Docker kernels create inert tunnel interfaces even with network=none.
    # Permit only known down devices, while checking routes and kernel privileges.
    links = {}
    for _, name in socket.if_nameindex():
        link = Path("/sys/class/net") / name
        links[name] = (int((link / "flags").read_text().strip(), 16), (link / "operstate").read_text().strip())
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    validate_network(links, Path("/proc/net/route").read_text().splitlines()[1:],
                     Path("/proc/net/ipv6_route").read_text().splitlines(),
                     int(status["CapEff"].strip(), 16), int(status["NoNewPrivs"].strip()))


def create_server():
    from fastmcp import FastMCP
    mcp = FastMCP("Synthetic local sandbox")
    store = Store("/workspace")
    lock = threading.Lock()

    def guarded(fn, *args):
        with lock:
            try:
                return fn(*args)
            except (ValueError, OSError, UnicodeError):
                # Do not return OS paths, tracebacks or excerpts of invalid data.
                return {"error": "operation_denied_or_invalid_input"}

    @mcp.tool
    def list_files() -> list[str]:
        """List at most 100 allowed synthetic text files."""
        return guarded(store.list)

    @mcp.tool
    def read_file(path: str) -> dict:
        """Read one UTF-8 file, at most 16 KiB, under samples/ or notes/."""
        result = guarded(store.read, path)
        return result if isinstance(result, dict) else {"path": path, "text": result}

    @mcp.tool
    def write_file(path: str, text: str, expected: str | None = None) -> dict:
        """Create a small text file; to replace one, supply its exact previous contents."""
        return guarded(store.write, path, text, expected)

    @mcp.tool
    def run_check(name: str) -> dict:
        """Run only sample_json or self_test. No shell, user code, arguments or model delegation."""
        if name == "sample_json":
            return guarded(store.check_json)
        if name != "self_test":
            return {"error": "check_not_allowed"}
        with lock:
            try:
                result = subprocess.run(
                    [sys.executable, "-I", "-S", "-B", "/opt/kit/src/selftest.py"],
                    capture_output=True, timeout=10, check=False,
                    env={"PATH": "/usr/local/bin:/usr/bin:/bin"}, cwd="/tmp")
                return {"check": name, "passed": result.returncode == 0}
            except (OSError, subprocess.TimeoutExpired):
                return {"check": name, "passed": False}
    return mcp


def main():
    verify_runtime()
    os.umask(0o077)
    if not select.select([sys.stdin], [], [], 15)[0]:
        raise ValueError("Session input timeout")
    raw = sys.stdin.buffer.readline(257)
    session = json.loads(raw)
    if set(session) != {"digest"} or len(raw) > 256:
        raise ValueError("Invalid session input")
    digest = bytes.fromhex(session["digest"])
    if len(digest) != 32:
        raise ValueError("Invalid digest")
    app = Auth(create_server().http_app(path="/mcp", transport="streamable-http",
                                       json_response=True, stateless_http=True), digest)
    import uvicorn
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind("/ipc/mcp.sock")
    os.chmod("/ipc/mcp.sock", 0o600)
    sock.listen(16)
    try:
        server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level="critical",
                                              timeout_keep_alive=2, timeout_graceful_shutdown=1))
        asyncio.run(server.serve(sockets=[sock]))
    finally:
        sock.close()
        Path("/ipc/mcp.sock").unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("Sandbox startup failed; details suppressed")
