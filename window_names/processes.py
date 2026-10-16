from pathlib import Path


class Process:
    def __init__(self, pid: int, proc: Path = Path("/proc")):
        self.pid = pid
        self._proc = proc

    @property
    def program(self) -> str:
        return self._read("comm").strip()

    @property
    def folder(self) -> Path | None:
        try:
            return (self._proc / str(self.pid) / "cwd").readlink()
        except OSError:
            return None

    def children(self) -> list["Process"]:
        task = self._proc / str(self.pid) / "task" / str(self.pid) / "children"
        try:
            return [Process(int(pid), self._proc) for pid in task.read_text().split()]
        except OSError:
            return []

    def in_front(self) -> "Process":
        shells = self.children()
        if not shells:
            return self
        shell = shells[0]
        group = shell.foreground_group()
        return Process(group, self._proc) if group > 0 else shell

    def foreground_group(self) -> int:
        stat = self._read("stat")
        after_name = stat[stat.rfind(")") + 2:].split()
        return int(after_name[5]) if len(after_name) > 5 else -1

    def _read(self, name: str) -> str:
        try:
            return (self._proc / str(self.pid) / name).read_text()
        except OSError:
            return ""
