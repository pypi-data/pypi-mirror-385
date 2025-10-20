import plistlib
from typing import Optional, Any

from rushlib.file import FileStream


class PlistStream(FileStream):
    @property
    def is_plist(self) -> bool:
        return self.suffix == ".json"

    def read(self) -> Optional[dict[str, Any]]:
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self.path, mode='rb', encoding='utf-8') as f:
            return plistlib.load(f)

    def write(self, data: dict, indent=4) -> None:
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self._path, 'wb', encoding="utf-8") as file:
            plistlib.dump(data, file)
