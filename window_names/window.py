from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    id: str
    app_class: str
    title: str
    pid: int
