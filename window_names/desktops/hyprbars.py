import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hyprland import Hyprland

HYPRBARS = Path.home() / "RiderProjects/hyprland-plugins/hyprbars"
HYPRLAND = Path("/usr/bin/Hyprland")


class Hyprbars:
    def __init__(self, hyprland: "Hyprland", source: Path = HYPRBARS, compositor: Path = HYPRLAND):
        self._hyprland = hyprland
        self._source = source
        self._compositor = compositor

    @property
    def plugin(self) -> Path:
        return self._source / "hyprbars.so"

    def load(self) -> None:
        if self._outdated() and not self._build():
            self._hyprland.ask(f"notify 3 15000 0 Title bars could not be rebuilt for this Hyprland version. Run: make -C {self._source}")
            return
        self._hyprland.ask(f"plugin load {self.plugin}")

    def _outdated(self) -> bool:
        return not self.plugin.exists() or self.plugin.stat().st_mtime < self._compositor.stat().st_mtime

    def _build(self) -> bool:
        return subprocess.run(["make", "-B", "-C", str(self._source), "all"], capture_output=True).returncode == 0
