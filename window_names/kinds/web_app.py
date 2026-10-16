import re

from ..window import Window

WEB_APP_CLASS = re.compile(r"^(?:chrome|chromium|brave|msedge)-([^_]+)__")


class WebApp:
    def matches(self, window: Window) -> bool:
        return WEB_APP_CLASS.match(window.app_class) is not None

    def name(self, window: Window) -> str:
        site = WEB_APP_CLASS.match(window.app_class).group(1)
        return site.removeprefix("www.")
