import json
from typing import Optional, Any

from rushlib.file import FileStream


class JsonStream(FileStream):
    @property
    def is_json(self) -> bool:
        return self.suffix == ".json"

    def read(self) -> Optional[dict[str, Any]]:
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self.path, mode='r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, data: dict, indent=4) -> None:
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self._path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
