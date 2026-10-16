import os
import re

from .i3_family import I3Family
from .i3_ipc import GET_CONFIG, I3Ipc

PANGO_FONT = re.compile(r"^\s*font\s+pango:", re.MULTILINE)


class Sway(I3Family):
    def __init__(self):
        super().__init__(I3Ipc(os.environ["SWAYSOCK"]))

    @staticmethod
    def is_running() -> bool:
        return "SWAYSOCK" in os.environ

    def reads_markup(self) -> bool:
        return PANGO_FONT.search(self._ipc.ask(GET_CONFIG).get("config", "")) is not None

    def holds_app(self, node: dict) -> bool:
        return "pid" in node and node.get("type") in ("con", "floating_con") and not node.get("nodes")

    def app_class(self, node: dict) -> str:
        return node.get("app_id") or node.get("window_properties", {}).get("class", "")

    def pid(self, node: dict) -> int:
        return node.get("pid") or 0
