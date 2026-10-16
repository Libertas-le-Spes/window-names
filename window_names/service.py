from .desktops.desktop import Desktop
from .namer import Namer


class Service:
    def __init__(self, desktop: Desktop, namer: Namer, refresh_seconds: float = 3):
        self._desktop = desktop
        self._namer = namer
        self._refresh_seconds = refresh_seconds
        self._open: set[str] = set()

    def run(self) -> None:
        self._desktop.prepare()
        while True:
            self.refresh()
            self._desktop.wait(self._refresh_seconds)

    def refresh(self) -> None:
        windows = self._desktop.windows()
        open_ids = {window.id for window in windows}
        for closed in self._open - open_ids:
            self._namer.forget(closed)
        self._open = open_ids
        for window in windows:
            self._desktop.show_text(window.id, self._namer.text_for(window))
