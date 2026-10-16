import sys
from pathlib import Path

from .app_names import AppNames
from .desktops.desktops import running_desktop
from .given_names import GivenNames
from .kinds.any_app import AnyApp
from .kinds.claude_terminal import ClaudeTerminal
from .kinds.jetbrains import JetBrains
from .kinds.terminal import Terminal
from .kinds.web_app import WebApp
from .namer import Namer
from .prompts.prompts import first_available
from .rename import Rename
from .service import Service

STATE = Path.home() / ".local/state"
BY_HAND = GivenNames(STATE / "window-names-by-hand")
BY_TOOLS = GivenNames(STATE / "window-names")


def namer() -> Namer:
    app_names = AppNames()
    terminal = Terminal()
    kinds = [ClaudeTerminal(terminal), terminal, JetBrains(app_names), WebApp(), AnyApp(app_names)]
    return Namer([BY_HAND, BY_TOOLS], kinds)


def main(command: str = "run") -> None:
    desktop = running_desktop()
    names = namer()
    commands = {
        "run": lambda: Service(desktop, names).run(),
        "rename": lambda: Rename(desktop, BY_HAND, names, first_available()).focused_window(),
        "show": lambda: [print(f"{w.id}  {names.text_for(w)}") for w in desktop.windows()],
    }
    commands[command]()


if __name__ == "__main__":
    main(*sys.argv[1:2])
