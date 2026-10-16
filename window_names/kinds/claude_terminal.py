import re

from ..folders import short_folder
from ..window import Window
from .terminal import Terminal

STATUS_MARK = re.compile(r"^[^\w~]+\s+")
APP_NAME = "Claude Code"


class ClaudeTerminal:
    def __init__(self, terminal: Terminal):
        self._terminal = terminal

    def matches(self, window: Window) -> bool:
        return self._terminal.matches(window) and self._terminal.in_front(window).program == "claude"

    def name(self, window: Window) -> str:
        folder = short_folder(self._terminal.in_front(window).folder)
        session = STATUS_MARK.sub("", window.title).strip()
        named = session and session != APP_NAME
        return f"{APP_NAME} — {folder} · {session}" if named else f"{APP_NAME} — {folder}"
