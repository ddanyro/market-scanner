"""Private, disposable research checkpoints. Never an authoritative ledger.

SQLite transactions keep completed batches readable after timeout/termination.
No pickle or executable deserialization; each compressed JSON record is hashed.
"""
from contextlib import AbstractContextManager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import zlib


def fingerprint(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(',', ':'), default=str,
    ).encode()).hexdigest()


class ResearchCache(AbstractContextManager):
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Create privately before SQLite opens it; never widen existing access.
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(descriptor)
        self.connection = sqlite3.connect(path, timeout=5)
        self.connection.execute('''CREATE TABLE IF NOT EXISTS checkpoints (
            namespace TEXT NOT NULL, key TEXT NOT NULL, digest TEXT NOT NULL,
            payload BLOB NOT NULL, PRIMARY KEY(namespace, key))''')
        self.pending = 0

    def get(self, namespace, key):
        row = self.connection.execute(
            'SELECT digest, payload FROM checkpoints WHERE namespace=? AND key=?',
            (namespace, key),
        ).fetchone()
        if row is None:
            return None
        try:
            raw = zlib.decompress(row[1])
            if hashlib.sha256(raw).hexdigest() != row[0]:
                return None
            return json.loads(raw)
        except (ValueError, UnicodeError, zlib.error):
            return None

    def put(self, namespace, key, value):
        raw = json.dumps(value, separators=(',', ':'), default=str).encode()
        self.connection.execute(
            'INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?, ?)',
            (namespace, key, hashlib.sha256(raw).hexdigest(), zlib.compress(raw)),
        )
        self.pending += 1
        if self.pending >= 64:
            self.flush()

    def flush(self):
        self.connection.commit()
        self.pending = 0

    def __exit__(self, *args):
        try:
            self.flush()
        finally:
            self.connection.close()

