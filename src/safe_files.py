"""Small, descriptor-relative text store. Linux runtime; no host path API."""
import json
import os
from pathlib import Path, PurePosixPath
import stat

MAX_TEXT = 16384
ALLOWED_DIRS = {"samples", "notes"}
ALLOWED_SUFFIXES = {".txt", ".md", ".json"}


class Denied(ValueError):
    pass


def parts(name):
    if not isinstance(name, str) or len(name) > 160 or "\\" in name:
        raise Denied("Invalid relative path")
    p = PurePosixPath(name)
    if p.is_absolute() or len(p.parts) != 2 or p.parts[0] not in ALLOWED_DIRS:
        raise Denied("Only samples/ and notes/ files are allowed")
    if str(p) != name or any(x.startswith(".") for x in p.parts):
        raise Denied("Hidden and traversing paths are denied")
    if p.suffix not in ALLOWED_SUFFIXES or any(ord(c) < 32 for c in name):
        raise Denied("Only small text, Markdown and JSON files are allowed")
    return p.parts


class Store:
    def __init__(self, root):
        self.root = Path(root)

    def directory(self, name):
        directory, filename = parts(name)
        root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        finally:
            os.close(root_fd)
        return fd, filename

    def read(self, name):
        directory, filename = self.directory(name)
        try:
            fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_TEXT:
                    raise Denied("File is not a bounded, unlinked regular text file")
                data = os.read(fd, MAX_TEXT + 1)
                if len(data) > MAX_TEXT or b"\x00" in data:
                    raise Denied("Text limit exceeded")
                return data.decode("utf-8")
            finally:
                os.close(fd)
        finally:
            os.close(directory)

    def write(self, name, text, expected=None):
        """Create or compare-and-replace; callers serialize operations with a lock."""
        if not isinstance(text, str) or "\x00" in text or len(text.encode("utf-8")) > MAX_TEXT:
            raise Denied("Text limit exceeded")
        directory, filename = self.directory(name)
        temporary = ".pending-write"
        try:
            # Replacement is opt-in and requires the exact previous contents.
            if expected is None:
                if len(self.list()) >= 100:
                    raise Denied("Workspace file limit reached")
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                fd = os.open(filename, flags, 0o600, dir_fd=directory)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(text.encode("utf-8"))
            else:
                if self.read(name) != expected:
                    raise Denied("Previous contents changed")
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(text.encode("utf-8"))
                    os.replace(temporary, filename, src_dir_fd=directory, dst_dir_fd=directory)
                finally:
                    try:
                        os.unlink(temporary, dir_fd=directory)
                    except FileNotFoundError:
                        pass
        finally:
            os.close(directory)
        return {"path": name, "bytes": len(text.encode("utf-8"))}

    def list(self):
        result = []
        for directory in sorted(ALLOWED_DIRS):
            fd, _ = self.directory(directory + "/placeholder.txt")
            try:
                filenames = sorted(os.listdir(fd))
            finally:
                os.close(fd)
            for filename in filenames:
                name = directory + "/" + filename
                try:
                    self.read(name)
                except (OSError, ValueError, UnicodeError):
                    continue
                result.append(name)
                if len(result) >= 100:
                    return result
        return result

    def check_json(self):
        data = json.loads(self.read("samples/example.json"))
        if not isinstance(data, dict) or set(data) != {"message", "count"}:
            raise Denied("Expected message and count fields")
        if not isinstance(data["message"], str) or type(data["count"]) is not int:
            raise Denied("Invalid example field types")
        return {"passed": True, "check": "sample_json"}
