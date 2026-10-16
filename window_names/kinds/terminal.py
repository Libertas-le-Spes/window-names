from collections.abc import Callable

from ..folders import short_folder
from ..processes import Process
from ..window import Window

TERMINAL_CLASSES = frozenset({"foot", "footclient", "alacritty", "kitty", "com.mitchellh.ghostty"})
SHELLS = frozenset({"bash", "zsh", "fish", "sh", "nu"})


class Terminal:
    def __init__(self, process: Callable[[int], Process] = Process, classes: frozenset[str] = TERMINAL_CLASSES):
        self._process = process
        self._classes = classes

    def matches(self, window: Window) -> bool:
        return window.app_class.lower() in self._classes

    def name(self, window: Window) -> str:
        front = self.in_front(window)
        program = "Terminal" if front.program in SHELLS else front.program
        return f"{program} — {short_folder(front.folder)}"

    def in_front(self, window: Window) -> Process:
        return self._process(window.pid).in_front()
