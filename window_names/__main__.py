import sys
from pathlib import Path

from .app_names import AppNames
from .given_names import GivenNames
from .hyprland import Hyprland
from .kinds.any_app import AnyApp
from .kinds.claude_terminal import ClaudeTerminal
from .kinds.jetbrains import JetBrains
from .kinds.terminal import Terminal
from .kinds.web_app import WebApp
from .menu_prompt import ask_in_menu
from .namer import Namer
from .rename import Rename
from .service import Service
from .title_bars import TitleBars

STATE = Path.home() / ".local/state"
BY_HAND = GivenNames(STATE / "window-names-by-hand")
BY_TOOLS = GivenNames(STATE / "window-names")


def namer() -> Namer:
    app_names = AppNames()
    terminal = Terminal()
    kinds = [ClaudeTerminal(terminal), terminal, JetBrains(app_names), WebApp(), AnyApp(app_names)]
    return Namer([BY_HAND, BY_TOOLS], kinds)


def main(command: str = "run") -> None:
    hyprland = Hyprland()
    names = namer()
    commands = {
        "run": lambda: (TitleBars(hyprland).load(), Service(hyprland, names).run()),
        "rename": lambda: Rename(hyprland, BY_HAND, names, ask_in_menu).focused_window(),
        "show": lambda: [print(f"{w.address}  {names.text_for(w)}") for w in hyprland.windows()],
    }
    commands[command]()


if __name__ == "__main__":
    main(*sys.argv[1:2])
