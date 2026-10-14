"""Build a source-only review ZIP from an explicit publication allowlist."""
import hashlib
import json
from pathlib import Path
import stat
import zipfile

FILES = (
    ".dockerignore", ".env.example", ".gitignore", "Dockerfile", "Dockerfile.gateway",
    "README.md", "LICENSE", "LICENSE-STATUS.md", "VERIFICATION.md", "launch.py", "package_review.py",
    "requirements.lock", "docs/PROVENANCE.md", "docs/SECURITY.md", "docs/RELEASE-CHECKLIST.md",
    "docs/dependency-license-inventory.json", "fixtures/samples/example.json",
    "fixtures/notes/welcome.md", "skills/notion-local-sandbox/SKILL.md",
    "src/auth.py", "src/gateway.py", "src/origin_proxy.py", "src/safe_files.py",
    "src/selftest.py", "src/server.py", "tests/test_safety.py",
)


def build(root, target):
    payloads, rows = {}, []
    for name in sorted(FILES):
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError("Symlink input rejected")
        if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_nlink != 1:
            raise ValueError("Only independent regular source files may be packaged")
        data = path.read_bytes()
        data.decode("utf-8")
        payloads[name] = data
        rows.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = (json.dumps({"status": "source-only distribution; project-owned files licensed under MIT", "files": rows}, indent=2) + "\n").encode()
    payloads["PUBLICATION-MANIFEST.json"] = manifest
    (root / "PUBLICATION-MANIFEST.json").write_bytes(manifest)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo("notion-local-sandbox/" + name, (2026, 10, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(payloads)
        for name, data in payloads.items():
            assert archive.read("notion-local-sandbox/" + name) == data
    return {"file_count": len(payloads), "zip_bytes": target.stat().st_size,
            "zip_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(json.dumps(build(root, root.parent / "notion-local-sandbox-review.zip")))
