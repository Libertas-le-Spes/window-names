from .desktops.desktop import Desktop
from .given_names import GivenNames
from .namer import Namer
from .prompts.prompt import Prompt


class Rename:
    def __init__(self, desktop: Desktop, by_hand: GivenNames, namer: Namer, prompt: Prompt):
        self._desktop = desktop
        self._by_hand = by_hand
        self._namer = namer
        self._prompt = prompt

    def focused_window(self) -> None:
        window = self._desktop.active_window()
        if window is None:
            return
        name = self._prompt.ask("Window name (empty for the default)")
        if name is None:
            return
        if name:
            self._by_hand.give(window.id, name)
        else:
            self._by_hand.forget(window.id)
        self._desktop.show_text(window.id, self._namer.text_for(window))
