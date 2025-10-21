import os
import shutil
from pathlib import Path
from typing import Optional, Iterator

from rushlib.path import MPath
from rushlib.types import path_type


class Stream:
    def __init__(self, path: path_type):
        self._path = MPath.to_path(path)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def copy(self, destination, ignore=None):
        if ignore is None:
            ignore = []

        source = MPath.to_path(self.path)
        destination = MPath.to_path(destination)

        FolderStream(destination).create()

        if not source.exists():
            return False

        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(*ignore),
            )
        else:
            shutil.copy(
                source,
                destination,
            )

        return True

    def delete(self):
        source = MPath.to_path(self.path)

        if source.is_dir():
            shutil.rmtree(source, ignore_errors=True)
        else:
            source.unlink(missing_ok=True)

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__} {self}]"


class FileStream(Stream):
    @property
    def suffix(self) -> str:
        return self.path.suffix

    def read(self) -> Optional[str]:
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, text: str):
        if not self.exists:
            raise FileNotFoundError("File not found")

        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def create(self, value: str = ""):
        if self.exists:
            return

        with open(self.path, "w", encoding="utf-8") as f:
            f.write(value)


class DirectoryInfo:
    def __init__(self, path, folders, files) -> None:
        self._path = os.path.normpath(path)
        self._folders = folders
        self._files = files

    def __iter__(self) -> Iterator:
        yield self._path
        yield self._folders
        yield self._files

    def __repr__(self) -> str:
        return f"<DirectoryInfo: {self._path}>"

    @property
    def path(self) -> str:
        return self._path

    @property
    def folders(self) -> list["FolderStream"]:
        return self._folders

    @property
    def files(self) -> list[FileStream]:
        return self._files


class FolderStream(Stream):
    def create(self):
        if self.exists:
            return self

        self.path.mkdir(parents=True, exist_ok=True)

        return self

    def walk(self) -> Optional[DirectoryInfo]:
        if not self.exists: return None

        folders = []
        files = []

        try:
            with os.scandir(self._path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        sub_folder = FolderStream(entry.path)
                        folders.append(sub_folder)
                    elif entry.is_file():
                        files.append(FileStream(entry.path))
        except PermissionError:
            pass

        return DirectoryInfo(self._path, folders, files)
