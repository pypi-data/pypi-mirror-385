import socket
from .exceptions import ConnectionError

class Connection:
    def __init__(self, host='127.0.0.1', port=6383, unix_socket=None):
        self.host = host
        self.port = port
        self.unix_socket = unix_socket
        self.socket = None
        self._connect()
    
    def _connect(self):
        try:
            if self.unix_socket:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.unix_socket)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
        except socket.error as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    def send(self, data: str):
        if not self.socket:
            raise ConnectionError("Not connected")
        try:
            self.socket.sendall(data.encode('utf-8'))
        except socket.error as e:
            raise ConnectionError(f"Send failed: {e}")
    
    def recv(self, buffer_size=4096) -> bytes:
        if not self.socket:
            raise ConnectionError("Not connected")
        try:
            return self.socket.recv(buffer_size)
        except socket.error as e:
            raise ConnectionError(f"Receive failed: {e}")
    
    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None