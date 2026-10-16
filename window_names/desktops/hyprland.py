import json
import os
import socket
from pathlib import Path

from ..window import Window
from .hyprbars import Hyprbars
from .sent_texts import SentTexts


class Hyprland:
    def __init__(self, runtime: Path | None = None):
        runtime = runtime or Path(os.environ["XDG_RUNTIME_DIR"]) / "hypr" / os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
        self._requests = str(runtime / ".socket.sock")
        self._events_path = str(runtime / ".socket2.sock")
        self._events: socket.socket | None = None
        self._sent = SentTexts()

    @staticmethod
    def is_running() -> bool:
        return "HYPRLAND_INSTANCE_SIGNATURE" in os.environ

    def prepare(self) -> None:
        Hyprbars(self).load()

    def windows(self) -> list[Window]:
        windows = [self._window(client) for client in json.loads(self.ask("j/clients"))]
        self._sent.keep_only({window.id for window in windows})
        return windows

    def active_window(self) -> Window | None:
        client = json.loads(self.ask("j/activewindow"))
        return self._window(client) if client.get("address") else None

    def show_text(self, window_id: str, text: str) -> bool:
        return self._sent.send(window_id, text, lambda to, shown: self.ask(f"hyprbars-text {to} {shown}") == "ok")

    def wait(self, seconds: float) -> None:
        if self._events is None:
            self._events = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._events.connect(self._events_path)
        self._events.settimeout(seconds)
        try:
            if not self._events.recv(65536):
                raise ConnectionError("Hyprland has stopped")
        except socket.timeout:
            pass

    def ask(self, request: str) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.connect(self._requests)
            connection.sendall(request.encode())
            return b"".join(iter(lambda: connection.recv(65536), b"")).decode()

    @staticmethod
    def _window(client: dict) -> Window:
        return Window(
            id=client["address"],
            app_class=client.get("class") or client.get("initialClass") or "",
            title=client.get("title") or "",
            pid=client.get("pid") or 0,
        )
