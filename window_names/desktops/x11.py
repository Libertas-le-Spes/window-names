import os
import shutil
import time

from ..window import Window
from .xprop import Xprop


class X11:
    def __init__(self, xprop: Xprop = Xprop(), sleep=time.sleep):
        self._xprop = xprop
        self._sleep = sleep
        self._shown: dict[str, str] = {}
        self._own_titles: dict[str, str] = {}

    @staticmethod
    def is_running() -> bool:
        return "DISPLAY" in os.environ and "WAYLAND_DISPLAY" not in os.environ and shutil.which("xprop") is not None

    def prepare(self) -> None:
        pass

    def windows(self) -> list[Window]:
        open_ids = self._xprop.client_ids()
        self._shown = {window_id: text for window_id, text in self._shown.items() if window_id in open_ids}
        self._own_titles = {window_id: title for window_id, title in self._own_titles.items() if window_id in open_ids}
        return [self._window(window_id) for window_id in open_ids]

    def active_window(self) -> Window | None:
        window_id = self._xprop.active_id()
        return self._window(window_id) if window_id else None

    def show_text(self, window_id: str, text: str) -> bool:
        if self._shown.get(window_id) == text:
            return True
        if not self._xprop.set_title(window_id, text):
            return False
        self._shown[window_id] = text
        return True

    def wait(self, seconds: float) -> None:
        self._sleep(min(seconds, 1))

    def _window(self, window_id: str) -> Window:
        classes = self._xprop.strings_of(window_id, "WM_CLASS")
        return Window(id=window_id, app_class=classes[-1] if classes else "", title=self._own_title(window_id), pid=self._xprop.pid_of(window_id))

    def _own_title(self, window_id: str) -> str:
        titles = self._xprop.strings_of(window_id, "_NET_WM_NAME") or self._xprop.strings_of(window_id, "WM_NAME")
        current = titles[0] if titles else ""
        if current != self._shown.get(window_id):
            self._own_titles[window_id] = current
            self._shown.pop(window_id, None)
        return self._own_titles.get(window_id, current)
