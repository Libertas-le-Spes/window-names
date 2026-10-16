import re
import subprocess

WINDOW_ID = re.compile(r"0x[0-9a-f]+")
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
NUMBER = re.compile(r"=\s*(\d+)")


class Xprop:
    def client_ids(self) -> list[str]:
        return WINDOW_ID.findall(self._root("_NET_CLIENT_LIST"))

    def active_id(self) -> str | None:
        found = WINDOW_ID.findall(self._root("_NET_ACTIVE_WINDOW"))
        return found[0] if found and found[0] != "0x0" else None

    def root_strings(self, name: str) -> list[str]:
        return [self._unescape(value) for value in QUOTED.findall(self._root(name))]

    def strings_of(self, window_id: str, name: str) -> list[str]:
        return [self._unescape(value) for value in QUOTED.findall(self._of(window_id, name))]

    def pid_of(self, window_id: str) -> int:
        found = NUMBER.search(self._of(window_id, "_NET_WM_PID"))
        return int(found.group(1)) if found else 0

    def set_title(self, window_id: str, text: str) -> bool:
        utf8 = self._run("-id", window_id, "-f", "_NET_WM_NAME", "8u", "-set", "_NET_WM_NAME", text)
        plain = self._run("-id", window_id, "-f", "WM_NAME", "8t", "-set", "WM_NAME", text)
        return utf8 is not None and plain is not None

    def _root(self, name: str) -> str:
        return self._run("-root", "-notype", name) or ""

    def _of(self, window_id: str, name: str) -> str:
        return self._run("-id", window_id, "-notype", name) or ""

    @staticmethod
    def _run(*arguments: str) -> str | None:
        try:
            done = subprocess.run(["xprop", *arguments], capture_output=True, text=True)
        except FileNotFoundError:
            return None
        return done.stdout if done.returncode == 0 else None

    @staticmethod
    def _unescape(value: str) -> str:
        return re.sub(r"\\(.)", r"\1", value)
