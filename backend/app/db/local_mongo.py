"""
Best-effort local MongoDB bootstrapper.

If the configured MONGODB_URI points at a local server (localhost / 127.0.0.1)
and nothing is listening there, this locates an installed `mongod` binary and
starts it against a project-local data directory. This makes the app work on a
dev machine where the MongoDB Windows service is disabled and MongoDB Atlas is
unreachable, without any manual steps.

It is a no-op for remote URIs (mongodb+srv://, Atlas, etc.).
"""
from __future__ import annotations
import atexit
import glob
import os
import shutil
import socket
import subprocess
import sys
import time
from typing import Optional
from urllib.parse import urlparse

_proc: Optional[subprocess.Popen] = None


def _is_local(uri: str) -> bool:
    if uri.startswith("mongodb+srv://") or "mongodb.net" in uri:
        return False
    try:
        host = urlparse(uri).hostname or ""
    except ValueError:
        return False
    return host in ("localhost", "127.0.0.1", "::1", "")


def _host_port(uri: str) -> tuple[str, int]:
    parsed = urlparse(uri)
    return (parsed.hostname or "127.0.0.1", parsed.port or 27017)


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    target = "127.0.0.1" if host in ("localhost", "") else host
    try:
        with socket.create_connection((target, port), timeout=timeout):
            return True
    except OSError:
        return False


def _find_mongod() -> Optional[str]:
    found = shutil.which("mongod")
    if found:
        return found
    patterns = [
        r"C:\Program Files\MongoDB\Server\*\bin\mongod.exe",
        r"C:\Program Files (x86)\MongoDB\Server\*\bin\mongod.exe",
        "/usr/bin/mongod",
        "/usr/local/bin/mongod",
        "/opt/homebrew/bin/mongod",
    ]
    hits: list[str] = []
    for pat in patterns:
        hits.extend(glob.glob(pat))
    # Prefer the highest version directory.
    hits.sort(reverse=True)
    return hits[0] if hits else None


def ensure_running(uri: str) -> bool:
    """Return True if a local server is reachable (started here or already up)."""
    global _proc
    if not _is_local(uri):
        return False

    host, port = _host_port(uri)
    if _port_open(host, port):
        return True

    mongod = _find_mongod()
    if not mongod:
        print("[local_mongo] no local MongoDB reachable and no 'mongod' binary found; "
              "install MongoDB or set MONGODB_URI to a reachable server.")
        return False

    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.getenv("LOCAL_MONGO_DBPATH", os.path.join(backend_dir, ".mongodb-data"))
    log_dir = os.path.join(data_dir, "logs")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    print(f"[local_mongo] starting mongod ({mongod}) on 127.0.0.1:{port}, dbpath={data_dir}")
    creationflags = 0
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        _proc = subprocess.Popen(
            [mongod, "--dbpath", data_dir, "--port", str(port),
             "--bind_ip", "127.0.0.1",
             "--logpath", os.path.join(log_dir, "mongod.log"), "--logappend"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    except OSError as e:
        print(f"[local_mongo] failed to launch mongod: {e}")
        return False

    atexit.register(_shutdown)

    for _ in range(40):  # up to ~20s
        if _proc.poll() is not None:
            print("[local_mongo] mongod exited during startup; check "
                  f"{os.path.join(log_dir, 'mongod.log')}")
            return False
        if _port_open("127.0.0.1", port):
            print("[local_mongo] mongod is up")
            return True
        time.sleep(0.5)

    print("[local_mongo] mongod did not accept connections in time")
    return False


def _shutdown() -> None:
    global _proc
    if _proc and _proc.poll() is None:
        _proc.terminate()
        try:
            _proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _proc.kill()
    _proc = None
