import socket

from .hyprland import Hyprland
from .namer import Namer

CLOSED = "closewindow>>"


class Service:
    def __init__(self, hyprland: Hyprland, namer: Namer, refresh_seconds: float = 3):
        self._hyprland = hyprland
        self._namer = namer
        self._refresh_seconds = refresh_seconds
        self._shown: dict[str, str] = {}

    def run(self) -> None:
        with self._hyprland.events() as events:
            events.settimeout(self._refresh_seconds)
            pending = b""
            while True:
                self.refresh()
                try:
                    chunk = events.recv(65536)
                except socket.timeout:
                    continue
                if not chunk:
                    return
                *lines, pending = (pending + chunk).split(b"\n")
                for line in lines:
                    self.on_event(line.decode(errors="replace"))

    def on_event(self, line: str) -> None:
        if line.startswith(CLOSED):
            address = "0x" + line.removeprefix(CLOSED)
            self._namer.forget(address)
            self._shown.pop(address, None)

    def refresh(self) -> None:
        for window in self._hyprland.windows():
            text = self._namer.text_for(window)
            if self._shown.get(window.address) != text and self._hyprland.show_text(window.address, text):
                self._shown[window.address] = text
