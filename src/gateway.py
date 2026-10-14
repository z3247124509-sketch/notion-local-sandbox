"""Optional public gateway. Accept secrets via bounded stdin; no raw logs."""
import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import time
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from origin_proxy import start_proxy


def configuration(payload):
    if not isinstance(payload, dict) or set(payload) != {"domain", "authtoken"}:
        raise ValueError("Invalid fields")
    domain, token = payload["domain"], payload["authtoken"]
    if not isinstance(domain, str) or not re.fullmatch(r"(?!-)[a-z0-9-]{1,63}(?<!-)\.ngrok-free\.(app|dev)", domain):
        raise ValueError("An account-assigned free domain is required")
    if not isinstance(token, str) or not token.strip() or len(token.encode()) > 1024:
        raise ValueError("Invalid token; value suppressed")
    if any(unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in token):
        raise ValueError("Invalid control characters; value suppressed")
    config = {"version": 3, "agent": {
        "authtoken": token, "remote_management": False, "update_check": False,
        "web_addr": False, "inspect_db_size": -1, "console_ui": False,
        "crl_noverify": False, "dns_resolver_ips": ["127.0.0.11"],
        "log": "stdout", "log_format": "json", "log_level": "error"}}
    return domain, config


def main():
    if os.geteuid() != 10001 or not Path("/.dockerenv").is_file():
        raise RuntimeError("Non-root container required")
    if not os.statvfs("/opt/kit").f_flag & os.ST_RDONLY:
        raise RuntimeError("Read-only root required")
    mounts = [line.split() for line in Path("/proc/mounts").read_text().splitlines()]
    if not any(row[1:3] == ["/state", "tmpfs"] for row in mounts):
        raise RuntimeError("Volatile secret storage required")
    if not select.select([sys.stdin], [], [], 15)[0]:
        raise ValueError("Session input timeout")
    raw = sys.stdin.buffer.readline(4097)
    if len(raw) > 4096:
        raise ValueError("Session input too large")
    domain, config = configuration(json.loads(raw))
    raw = None
    path = Path("/state/ngrok.json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(config, stream)
    config = None
    child = proxy = None
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        for _ in range(50):
            if Path("/ipc/mcp.sock").is_socket():
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("Origin unavailable")
        proxy = start_proxy()
        child = subprocess.Popen([
            "/usr/local/bin/ngrok", "http", "http://127.0.0.1:8767",
            "--url=https://" + domain, "--inspect=false", "--config=" + str(path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin"})
        while not stopping and child.poll() is None:
            time.sleep(0.2)
        if not stopping and child.returncode != 0:
            raise RuntimeError("Gateway failed")
    finally:
        if child and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        if proxy:
            proxy.shutdown()
            proxy.server_close()
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("Gateway failed; credential-bearing diagnostics suppressed")
