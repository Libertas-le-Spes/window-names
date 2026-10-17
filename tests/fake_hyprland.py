import socket
import tempfile
import threading
from pathlib import Path


class FakeHyprland:
    def __init__(self, reply: str = "ok"):
        self.reply = reply
        self.requests: list[str] = []
        self.runtime = Path(tempfile.mkdtemp())
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(self.runtime / ".socket.sock"))
        self._server.listen()
        threading.Thread(target=self._accept, daemon=True).start()

    def _accept(self) -> None:
        while True:
            connection, _ = self._server.accept()
            with connection:
                self.requests.append(connection.recv(65536).decode())
                connection.sendall(self.reply.encode())
