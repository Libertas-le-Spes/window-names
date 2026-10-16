from collections.abc import Callable


class SentTexts:
    def __init__(self):
        self._sent: dict[str, str] = {}

    def send(self, window_id: str, text: str, sender: Callable[[str, str], bool]) -> bool:
        if self._sent.get(window_id) == text:
            return True
        if not sender(window_id, text):
            return False
        self._sent[window_id] = text
        return True

    def keep_only(self, open_ids: set[str]) -> None:
        self._sent = {window_id: text for window_id, text in self._sent.items() if window_id in open_ids}
