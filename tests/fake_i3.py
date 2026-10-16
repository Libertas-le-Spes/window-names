import json
import socket
import struct
import tempfile
import threading
from pathlib import Path

HEADER = struct.Struct("=II")


class FakeI3:
    def __init__(self, tree: dict, config: str = ""):
        self.tree = tree
        self.config = config
        self.commands: list[str] = []
        self.path = str(Path(tempfile.mkdtemp()) / "ipc.sock")
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(self.path)
        self._server.listen()
        self._subscribers: list[socket.socket] = []
        threading.Thread(target=self._accept, daemon=True).start()

    def send_event(self) -> None:
        for subscriber in self._subscribers:
            self._reply(subscriber, 0x80000003, {"change": "title"})

    def _accept(self) -> None:
        while True:
            connection, _ = self._server.accept()
            threading.Thread(target=self._serve, args=(connection,), daemon=True).start()

    def _serve(self, connection: socket.socket) -> None:
        while header := connection.recv(14):
            length, kind = HEADER.unpack(header[6:])
            payload = connection.recv(length).decode() if length else ""
            self._answer(connection, kind, payload)

    def _answer(self, connection: socket.socket, kind: int, payload: str) -> None:
        if kind == 4:
            self._reply(connection, kind, self.tree)
        elif kind == 0:
            self.commands.append(payload)
            self._reply(connection, kind, [{"success": True}])
        elif kind == 9:
            self._reply(connection, kind, {"config": self.config})
        elif kind == 2:
            self._subscribers.append(connection)
            self._reply(connection, kind, {"success": True})

    @staticmethod
    def _reply(connection: socket.socket, kind: int, body) -> None:
        data = json.dumps(body).encode()
        connection.sendall(b"i3-ipc" + HEADER.pack(len(data), kind) + data)
