from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    address: str
    app_class: str
    title: str
    pid: int

    @classmethod
    def from_client(cls, client: dict) -> "Window":
        return cls(
            address=client["address"],
            app_class=client.get("class") or client.get("initialClass") or "",
            title=client.get("title") or "",
            pid=client.get("pid") or 0,
        )
