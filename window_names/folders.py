from pathlib import Path


def short_folder(folder: Path | None, home: Path = Path.home()) -> str:
    if folder is None:
        return ""
    if folder == home:
        return "~"
    if folder.is_relative_to(home):
        return "~/" + str(folder.relative_to(home))
    return str(folder)
