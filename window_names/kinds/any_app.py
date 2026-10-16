from ..app_names import AppNames
from ..window import Window


class AnyApp:
    def __init__(self, app_names: AppNames):
        self._app_names = app_names

    def matches(self, window: Window) -> bool:
        return True

    def name(self, window: Window) -> str:
        app = self._app_names.name_of(window.app_class) or window.title
        shows_more = window.title and window.title != app
        return f"{app} — {window.title}" if shows_more else app
