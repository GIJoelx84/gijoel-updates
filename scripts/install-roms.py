#!/usr/bin/env python3
"""Install verified ROM downloads listed in a cabinet profile."""
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener


EXTENSIONS = {"nes": {".nes", ".zip"}, "mame-libretro": {".zip"}}
CHUNK_SIZE = 65536


def check_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("ROM URLs must use HTTPS without embedded credentials")


class HTTPSRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        check_url(url)
        return super().redirect_request(request, response, code, message, headers, url)


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def install(manifest_path, root):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["version"] != 1 or not isinstance(manifest["roms"], list):
        raise ValueError("Expected a version 1 ROM manifest")

    pending = []
    seen = set()
    for entry in manifest["roms"]:
        system, name = entry["system"], entry["filename"]
        size, checksum, url = entry["bytes"], entry["sha256"], entry["url"]
        if (system not in EXTENSIONS or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._()'&+!,\-]*", name)
                or Path(name).suffix.lower() not in EXTENSIONS[system]):
            raise ValueError("Unsupported ROM destination")
        if type(size) is not int or size <= 0 or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise ValueError("Invalid ROM size or SHA-256")
        check_url(url)
        destination = root / system / name
        if destination in seen:
            raise ValueError("Duplicate ROM destination: " + name)
        seen.add(destination)
        if destination.parent.resolve() != destination.parent:
            raise ValueError("ROM system directory must not be a symlink")
        if destination.is_symlink():
            raise ValueError("ROM destination must not be a symlink: " + name)
        if destination.exists():
            if not destination.is_file() or destination.stat().st_size != size or digest(destination) != checksum:
                raise ValueError("Existing ROM differs from manifest: " + name)
            print("Verified existing ROM: " + name)
        else:
            pending.append((destination, size, checksum, url))

    opener = build_opener(HTTPSRedirects())
    staged = []
    try:
        for destination, size, checksum, url in pending:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=str(destination.parent), prefix=".rom-", delete=False) as output:
                path = Path(output.name)
                staged.append((path, destination))
                received = 0
                actual = hashlib.sha256()
                with opener.open(url, timeout=30) as response:
                    for chunk in iter(lambda: response.read(CHUNK_SIZE), b""):
                        received += len(chunk)
                        if received > size:
                            raise ValueError("Download exceeds declared size: " + destination.name)
                        actual.update(chunk)
                        output.write(chunk)
                if received != size or actual.hexdigest() != checksum:
                    raise ValueError("Download failed verification: " + destination.name)
        for path, destination in staged:
            os.chmod(str(path), 0o644)
            os.link(str(path), str(destination))
            print("Installed ROM: " + destination.name)
    finally:
        for path, _ in staged:
            path.unlink()


if __name__ == "__main__":
    try:
        install(Path(sys.argv[1]), Path(sys.argv[2]).resolve())
    except (OSError, ValueError, TypeError, KeyError) as error:
        sys.exit("ROM install failed: " + str(error))

