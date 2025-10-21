from __future__ import annotations
from typing import Optional
from .connection import Connection
from .exceptions import AuthError, ConnectionError


class Client:
    def __init__(self, host='127.0.0.1', port=6383, unix_socket=None, password=None):
        self.conn = Connection(host, port, unix_socket)
        if password:
            self.auth(password)

    def _send(self, cmd: str) -> str:
        self.conn.send(cmd + '\n')
        resp = self._recv_line().strip()
        return resp.decode() if isinstance(resp, bytes) else resp

    def _recv_line(self) -> bytes:
        """Read until newline from the connection socket."""
        if not self.conn.socket:
            raise ConnectionError("Not connected")
        data = b""
        while True:
            chunk = self.conn.socket.recv(1024)
            if not chunk:
                raise ConnectionError("Connection closed by server")
            data += chunk
            if b'\n' in chunk:
                break
        return data

    def auth(self, password: str) -> bool:
        resp = self._send(f"AUTH {password}")
        if resp != '+OK':
            raise AuthError(f"Authentication failed: {resp}")
        return True

    def set(self, key: str, value: str) -> bool:
        resp = self._send(f"SET '{key}' '{value}'")
        return resp == '+OK'

    def get(self, key: str) -> Optional[str]:
        resp = self._send(f"GET '{key}'")
        return None if resp == 'NONE' else resp

    def delete(self, key: str) -> bool:
        resp = self._send(f"DELETE {key}")
        return resp == '+OK'

    def exists(self, key: str) -> bool:
        resp = self._send(f"EXISTS {key}")
        return resp == '1'

    def ping(self) -> bool:
        resp = self._send("PING")
        return resp == '+PONG'

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()
