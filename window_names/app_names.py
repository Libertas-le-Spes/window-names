import configparser
from functools import cache
from pathlib import Path

DESKTOP_FOLDERS = (
    Path.home() / ".local/share/applications",
    Path("/usr/local/share/applications"),
    Path("/usr/share/applications"),
)


class AppNames:
    def __init__(self, folders: tuple[Path, ...] = DESKTOP_FOLDERS):
        self._folders = folders

    def name_of(self, app_class: str) -> str:
        return self._names().get(app_class.lower(), app_class)

    @cache
    def _names(self) -> dict[str, str]:
        names: dict[str, str] = {}
        for folder in reversed(self._folders):
            for entry in sorted(folder.glob("*.desktop")) if folder.is_dir() else ():
                names.update(self._read(entry))
        return names

    def _read(self, entry: Path) -> dict[str, str]:
        parser = configparser.RawConfigParser(strict=False, interpolation=None)
        try:
            parser.read(entry, encoding="utf-8")
            desktop = parser["Desktop Entry"]
        except (configparser.Error, KeyError, UnicodeDecodeError):
            return {}
        name = desktop.get("Name")
        if not name:
            return {}
        keys = {entry.stem.lower(), desktop.get("StartupWMClass", "").lower()} - {""}
        return {key: name for key in keys}
