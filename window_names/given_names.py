import os
import tempfile
from pathlib import Path


class GivenNames:
    def __init__(self, folder: Path):
        self.folder = folder

    def name_of(self, address: str) -> str | None:
        try:
            return (self.folder / address).read_text().strip() or None
        except OSError:
            return None

    def give(self, address: str, name: str) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=self.folder, prefix=".writing-", delete=False) as written:
            written.write(name.strip() + "\n")
        os.replace(written.name, self.folder / address)

    def forget(self, address: str) -> None:
        (self.folder / address).unlink(missing_ok=True)
