import json
import os
import socket
from pathlib import Path

from .window import Window


class Hyprland:
    def __init__(self, runtime: Path | None = None):
        runtime = runtime or Path(os.environ["XDG_RUNTIME_DIR"]) / "hypr" / os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
        self._requests = str(runtime / ".socket.sock")
        self._events = str(runtime / ".socket2.sock")

    def windows(self) -> list[Window]:
        return [Window.from_client(client) for client in json.loads(self._ask("j/clients"))]

    def active_window(self) -> Window | None:
        client = json.loads(self._ask("j/activewindow"))
        return Window.from_client(client) if client.get("address") else None

    def show_text(self, address: str, text: str) -> bool:
        return self._ask(f"hyprbars-text {address} {text}") == "ok"

    def load_plugin(self, plugin: Path) -> None:
        self._ask(f"plugin load {plugin}")

    def notify(self, message: str) -> None:
        self._ask(f"notify 3 15000 0 {message}")

    def events(self) -> socket.socket:
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.connect(self._events)
        return connection

    def _ask(self, request: str) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.connect(self._requests)
            connection.sendall(request.encode())
            return b"".join(iter(lambda: connection.recv(65536), b"")).decode()

