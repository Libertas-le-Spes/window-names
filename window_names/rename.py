from collections.abc import Callable

from .given_names import GivenNames
from .hyprland import Hyprland
from .namer import Namer


class Rename:
    def __init__(self, hyprland: Hyprland, by_hand: GivenNames, namer: Namer, ask: Callable[[str], str | None]):
        self._hyprland = hyprland
        self._by_hand = by_hand
        self._namer = namer
        self._ask = ask

    def focused_window(self) -> None:
        window = self._hyprland.active_window()
        if window is None:
            return
        name = self._ask("Window name (empty for the default)")
        if name is None:
            return
        if name:
            self._by_hand.give(window.address, name)
        else:
            self._by_hand.forget(window.address)
        self._hyprland.show_text(window.address, self._namer.text_for(window))
