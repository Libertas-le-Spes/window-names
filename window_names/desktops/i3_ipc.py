import json
import socket
import struct

MAGIC = b"i3-ipc"
HEADER = struct.Struct("=II")
RUN_COMMAND = 0
SUBSCRIBE = 2
GET_TREE = 4
GET_CONFIG = 9


class I3Ipc:
    def __init__(self, path: str):
        self._path = path
        self._events: socket.socket | None = None

    def ask(self, kind: int, payload: str = ""):
        with self._connect() as connection:
            self._send(connection, kind, payload)
            return json.loads(self._receive(connection))

    def wait_for_event(self, seconds: float) -> None:
        if self._events is None:
            self._events = self._connect()
            self._send(self._events, SUBSCRIBE, json.dumps(["window"]))
            self._receive(self._events)
        self._events.settimeout(seconds)
        try:
            self._receive(self._events)
        except socket.timeout:
            pass

    def _connect(self) -> socket.socket:
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.connect(self._path)
        return connection

    @staticmethod
    def _send(connection: socket.socket, kind: int, payload: str) -> None:
        body = payload.encode()
        connection.sendall(MAGIC + HEADER.pack(len(body), kind) + body)

    @classmethod
    def _receive(cls, connection: socket.socket) -> bytes:
        header = cls._exactly(connection, len(MAGIC) + HEADER.size)
        length, _ = HEADER.unpack(header[len(MAGIC):])
        return cls._exactly(connection, length)

    @staticmethod
    def _exactly(connection: socket.socket, size: int) -> bytes:
        data = b""
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("the window manager has stopped")
            data += chunk
        return data
