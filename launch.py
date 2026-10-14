"""Explicit local operator CLI. Never discovers credentials or pulls images."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "src"))
from auth import bearer_digest
from gateway import configuration

LABEL = "community.notion-sandbox.session"


def image_id(value):
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError("Use an inspected local image ID, never a tag")
    return value


def run_args(name, session, image, ipc, data=None):
    args = ["create", "--name", name, "--label", LABEL + "=" + session,
            "--pull=never", "--platform=linux/arm64", "--init", "--read-only",
            "--user=10001:10001", "--cap-drop=ALL", "--security-opt=no-new-privileges=true",
            "--cpus=1", "--memory=256m", "--memory-swap=256m", "--pids-limit=96",
            "--ulimit=core=0", "--log-driver=none", "--restart=no", "-i",
            "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m,uid=10001,gid=10001,mode=0700"]
    if data:
        args += ["--network=none", "--mount", "type=volume,src=" + data + ",dst=/workspace",
                 "--mount", "type=volume,src=" + ipc + ",dst=/ipc"]
    else:
        args += ["--network=bridge", "--mount", "type=volume,src=" + ipc + ",dst=/ipc,readonly,volume-nocopy",
                 "--tmpfs", "/state:rw,noexec,nosuid,nodev,size=1m,uid=10001,gid=10001,mode=0700"]
    return args + [image_id(image)]


def secret(prompt):
    if not sys.stdin.isatty():
        raise ValueError("Use a local interactive terminal; do not pipe or chat credentials")
    # Fail rather than accepting getpass's visible-input fallback.
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        return getpass.getpass(prompt)


class Docker:
    def __init__(self, executable, host, runtime):
        if not Path(executable).is_absolute() or not host.startswith("unix:///"):
            raise ValueError("Explicit Docker executable and local Unix socket required")
        if runtime.is_symlink():
            raise ValueError("Runtime directory must not be a symlink")
        runtime.mkdir(mode=0o700, exist_ok=True)
        config = runtime / "empty-docker-config"
        if config.is_symlink():
            raise ValueError("Invalid isolated Docker config")
        config.mkdir(mode=0o700, exist_ok=True)
        if any(config.iterdir()):
            raise ValueError("Docker config must stay empty; never use existing login configuration")
        self.prefix = [executable, "--config", str(config), "--host", host]
        self.env = {"PATH": "/usr/local/bin:/usr/bin:/bin"}

    def call(self, args, check=True):
        result = subprocess.run(self.prefix + args, capture_output=True, text=True,
                                env=self.env, timeout=20)
        if check and result.returncode:
            raise RuntimeError("Docker operation failed; raw diagnostics suppressed")
        return result

    def attach(self, name, payload):
        child = subprocess.Popen(self.prefix + ["start", "--attach", "--interactive", name],
                                 stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, env=self.env)
        try:
            child.stdin.write((json.dumps(payload) + "\n").encode())
            child.stdin.close()
        except Exception:
            child.terminate()
            child.wait(timeout=5)
            raise
        return child

    def owns(self, kind, name, session):
        template = '{{index .Config.Labels "' + LABEL + '"}}' if kind == "container" else '{{index .Labels "' + LABEL + '"}}'
        result = self.call([kind, "inspect", "--format", template, name], check=False)
        return result.returncode == 0 and result.stdout.strip() == session


def stop(docker, state):
    failed = False
    for name in reversed(state["containers"]):
        try:
            if docker.owns("container", name, state["session"]):
                docker.call(["container", "rm", "--force", name])
        except Exception:
            failed = True
    # A failed inspection must not turn Docker unavailability into false success.
    remaining = docker.call(["container", "ls", "--all", "--filter",
                             "label=" + LABEL + "=" + state["session"], "--format", "{{.Names}}"])
    if failed or remaining.stdout.strip():
        raise RuntimeError("Session stop not confirmed; retain state and retry stop")


def controlled_exit(signum, frame):
    raise KeyboardInterrupt


def install_exit_handlers():
    for signum in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, controlled_exit)


def load_state(path):
    if path.is_symlink() or path.stat().st_size > 2048:
        raise ValueError("Invalid session state")
    state = json.loads(path.read_text())
    session = state.get("session", "")
    if not re.fullmatch(r"[0-9a-f]{32}", session):
        raise ValueError("Invalid session identity")
    prefix = "notion-sandbox-" + session
    if state.get("containers") not in ([prefix + "-control"], [prefix + "-control", prefix + "-gateway"]):
        raise ValueError("Invalid container names")
    if state.get("volumes") != [prefix + "-ipc", prefix + "-data"]:
        raise ValueError("Invalid volume names")
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["offline", "remote", "stop", "purge"])
    parser.add_argument("--docker", required=True, help="Absolute path to the installed Docker CLI")
    parser.add_argument("--host", required=True, help="Explicit local unix:///... socket")
    parser.add_argument("--control-image")
    parser.add_argument("--gateway-image")
    parser.add_argument("--domain")
    parser.add_argument("--approved-public-session", action="store_true")
    parser.add_argument("--confirm-delete-synthetic-data", action="store_true")
    args = parser.parse_args()
    runtime = BASE / "runtime"
    docker = Docker(args.docker, args.host, runtime)
    state_path = runtime / "session.json"
    if args.action in {"stop", "purge"}:
        state = load_state(state_path)
        stop(docker, state)
        if args.action == "purge":
            if not args.confirm_delete_synthetic_data:
                raise ValueError("Data retained. Explicit deletion flag required")
            for name in state["volumes"]:
                if docker.owns("volume", name, state["session"]):
                    docker.call(["volume", "rm", name])
            remaining = docker.call(["volume", "ls", "--filter", "label=" + LABEL + "=" + state["session"],
                                     "--format", "{{.Name}}"])
            if remaining.stdout.strip():
                raise RuntimeError("Volume deletion not confirmed")
            state_path.unlink()
        print("Session stopped; unrelated Docker resources unchanged")
        return
    if state_path.exists() or state_path.is_symlink():
        raise ValueError("Existing session record; inspect and explicitly stop/purge before another run")
    control_image = image_id(args.control_image or "")
    remote = args.action == "remote"
    if remote and not args.approved_public_session:
        raise ValueError("Public access requires a separate, explicit approval")
    gateway_image = image_id(args.gateway_image or "") if remote else None
    for image in [control_image] + ([gateway_image] if remote else []):
        docker.call(["image", "inspect", "--format", "{{.Id}}", image])
    digest = bearer_digest(secret("User-supplied MCP Bearer token (hidden): ")).hex()
    gateway_payload = None
    if remote:
        gateway_payload = {"domain": args.domain, "authtoken": secret("ngrok Authtoken (hidden): ")}
        configuration(gateway_payload)
    session = uuid.uuid4().hex  # Resource identity, not an authentication secret.
    prefix = "notion-sandbox-" + session
    state = {"session": session,
             "containers": [prefix + "-control"] + ([prefix + "-gateway"] if remote else []),
             "volumes": [prefix + "-ipc", prefix + "-data"]}
    with state_path.open("x") as stream:
        os.chmod(state_path, 0o600)
        json.dump(state, stream)
    children = []
    install_exit_handlers()
    try:
        for name in state["volumes"]:
            docker.call(["volume", "create", "--label", LABEL + "=" + session, name])
        control = state["containers"][0]
        docker.call(run_args(control, session, control_image, *state["volumes"]))
        children.append(docker.attach(control, {"digest": digest}))
        if remote:
            gateway = state["containers"][1]
            docker.call(run_args(gateway, session, gateway_image, state["volumes"][0]))
            children.append(docker.attach(gateway, gateway_payload))
            gateway_payload = None
        print("Session processes started; connection success is not yet verified. Ctrl+C stops this session.")
        if remote:
            print("Configured MCP endpoint: https://" + args.domain + "/mcp")
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        raise RuntimeError("A session process exited; inspect the documented checks")
    except KeyboardInterrupt:
        print("Stopping this session")
    finally:
        # Complete bounded cleanup even if a second ordinary stop signal arrives.
        for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            signal.signal(signum, signal.SIG_IGN)
        stop(docker, state)
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.terminate()
        print("Synthetic volumes retained; use explicit purge only after reviewing their contents")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("Operation failed; no credential-bearing diagnostic output. See README troubleshooting.")
