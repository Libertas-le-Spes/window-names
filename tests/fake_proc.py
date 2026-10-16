from pathlib import Path


def add_process(proc: Path, pid: int, program: str, folder: Path, children: list[int] = (), foreground: int = 0) -> None:
    entry = proc / str(pid)
    (entry / "task" / str(pid)).mkdir(parents=True)
    (entry / "comm").write_text(program + "\n")
    (entry / "cwd").symlink_to(folder)
    (entry / "task" / str(pid) / "children").write_text(" ".join(map(str, children)))
    (entry / "stat").write_text(f"{pid} ({program}) S 1 {pid} {pid} 34816 {foreground} 4194560")
