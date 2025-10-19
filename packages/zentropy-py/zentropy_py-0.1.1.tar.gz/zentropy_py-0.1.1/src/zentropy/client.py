from __future__ import annotations
from typing import Optional
from .connection import Connection
from .exceptions import AuthError

class Client:
    def __init__(self, host='127.0.0.1', port=6383, unix_socket=None, password=None):
        self.conn = Connection(host, port, unix_socket)
        if password:
            self.auth(password)

    def _send(self, cmd: str) -> bytes:
        self.conn.send(cmd + '\n')
        resp = self.conn.recv().strip()
        return resp

    def auth(self, password: str) -> bool:
        resp = self._send(f"AUTH {password}")
        if resp != b'+OK':
            raise AuthError(f"Authentication failed: {resp.decode()}")
        return True

    def set(self, key: str, value: str) -> bool:
        resp = self._send(f"SET {key} '{value}'")
        return resp == b'OK'

    def get(self, key: str) -> Optional[str]:
        resp = self._send(f"GET {key}")
        if resp == b'NIL':
            return None
        return resp.decode()

    def delete(self, key: str) -> bool:
        resp = self._send(f"DELETE {key}")
        return resp == b'+OK'

    def exists(self, key: str) -> bool:
        resp = self._send(f"EXISTS {key}")
        return resp == b'1'

    def ping(self) -> bool:
        resp = self._send("PING")
        return resp == b'+PONG'

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()