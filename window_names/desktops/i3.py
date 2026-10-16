import os

from .i3_family import I3Family
from .i3_ipc import I3Ipc
from .xprop import Xprop


def socket_path(xprop: Xprop) -> str:
    if "I3SOCK" in os.environ:
        return os.environ["I3SOCK"]
    if "DISPLAY" not in os.environ or "WAYLAND_DISPLAY" in os.environ:
        return ""
    found = xprop.root_strings("I3_SOCKET_PATH")
    return found[0] if found else ""


class I3(I3Family):
    def __init__(self, xprop: Xprop = Xprop()):
        super().__init__(I3Ipc(socket_path(xprop)))
        self._xprop = xprop

    @staticmethod
    def is_running() -> bool:
        return bool(socket_path(Xprop()))

    def reads_markup(self) -> bool:
        return True

    def holds_app(self, node: dict) -> bool:
        return bool(node.get("window"))

    def app_class(self, node: dict) -> str:
        return node.get("window_properties", {}).get("class", "")

    def pid(self, node: dict) -> int:
        return self._xprop.pid_of(hex(node["window"]))
