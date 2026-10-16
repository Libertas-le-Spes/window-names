from typing import Protocol


class Prompt(Protocol):
    def is_available(self) -> bool: ...

    def ask(self, question: str) -> str | None: ...
