import html
from collections.abc import Iterator

from ..window import Window
from .i3_ipc import GET_TREE, RUN_COMMAND, I3Ipc
from .sent_texts import SentTexts


class I3Family:
    def __init__(self, ipc: I3Ipc):
        self._ipc = ipc
        self._sent = SentTexts()

    def prepare(self) -> None:
        pass

    def windows(self) -> list[Window]:
        windows = [self._window(node) for node in self._app_nodes()]
        self._sent.keep_only({window.id for window in windows})
        return windows

    def active_window(self) -> Window | None:
        return next((self._window(node) for node in self._app_nodes() if node.get("focused")), None)

    def show_text(self, window_id: str, text: str) -> bool:
        return self._sent.send(window_id, text, self._set_title_format)

    def _set_title_format(self, window_id: str, text: str) -> bool:
        shown = html.escape(text, quote=False) if self.reads_markup() else text
        quoted = shown.replace("\\", "\\\\").replace('"', '\\"')
        replies = self._ipc.ask(RUN_COMMAND, f'[con_id={window_id}] title_format "{quoted}"')
        return all(reply.get("success") for reply in replies)

    def wait(self, seconds: float) -> None:
        self._ipc.wait_for_event(seconds)

    def _app_nodes(self) -> Iterator[dict]:
        pending = [self._ipc.ask(GET_TREE)]
        while pending:
            node = pending.pop()
            pending.extend(node.get("nodes", []) + node.get("floating_nodes", []))
            if self.holds_app(node):
                yield node

    def _window(self, node: dict) -> Window:
        return Window(id=str(node["id"]), app_class=self.app_class(node), title=node.get("name") or "", pid=self.pid(node))

    def holds_app(self, node: dict) -> bool:
        raise NotImplementedError

    def reads_markup(self) -> bool:
        raise NotImplementedError

    def app_class(self, node: dict) -> str:
        raise NotImplementedError

    def pid(self, node: dict) -> int:
        raise NotImplementedError
