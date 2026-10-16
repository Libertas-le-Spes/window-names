from typing import Protocol

from .given_names import GivenNames
from .window import Window


class Kind(Protocol):
    def matches(self, window: Window) -> bool: ...

    def name(self, window: Window) -> str: ...


class Namer:
    def __init__(self, given: list[GivenNames], kinds: list[Kind]):
        self._given = given
        self._kinds = kinds

    def text_for(self, window: Window) -> str:
        given = (names.name_of(window.address) for names in self._given)
        return next(filter(None, given), None) or self._default_for(window)

    def forget(self, address: str) -> None:
        for names in self._given:
            names.forget(address)

    def _default_for(self, window: Window) -> str:
        return next(kind for kind in self._kinds if kind.matches(window)).name(window)
