from ..app_names import AppNames
from ..window import Window

TITLE_SEPARATOR = " – "


class JetBrains:
    def __init__(self, app_names: AppNames):
        self._app_names = app_names

    def matches(self, window: Window) -> bool:
        return window.app_class.startswith("jetbrains-") and TITLE_SEPARATOR in window.title

    def name(self, window: Window) -> str:
        project = window.title.split(TITLE_SEPARATOR, 1)[0]
        return f"{self._app_names.name_of(window.app_class)} — {project}"
