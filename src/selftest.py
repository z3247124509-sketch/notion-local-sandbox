"""Immutable self-test: never imports or executes files from /workspace."""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from safe_files import Denied, Store, parts


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "samples").mkdir()
        (root / "notes").mkdir()
        store = Store(root)
        store.write("samples/example.json", '{"message":"synthetic","count":1}')
        assert store.check_json()["passed"]
        store.write("notes/result.txt", "before")
        store.write("notes/result.txt", "after", "before")
        assert store.read("notes/result.txt") == "after"
        for path in ("/etc/passwd", "../secret.txt", "notes/.env", "samples/sub/a.txt"):
            try:
                parts(path)
            except Denied:
                continue
            raise AssertionError("Boundary failed")
    print(json.dumps({"passed": True}))


if __name__ == "__main__":
    main()
