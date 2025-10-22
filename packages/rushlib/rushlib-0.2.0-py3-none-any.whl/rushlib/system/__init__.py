import os
import platform
import subprocess
from pathlib import Path
from typing import Union, Optional


class SystemConsole:
    COMMAND_DICT: dict[str, dict[str, Union[str, list[str]]]] = {
        "python_venv": {
            "Windows": "Scripts",
            "Darwin": "bin",
            "Linux": "bin"
        },
        'clear': {
            'Windows': 'cls',
            'Linux': 'clear',
            'Darwin': 'clear'
        }
    }

    @classmethod
    def exe(cls, file):
        return f"{file}.exe" if cls.windows() else file

    @classmethod
    def os(cls):
        return platform.system()

    @classmethod
    def windows(cls):
        return cls.os() == "Windows"

    @classmethod
    def macos(cls):
        return cls.os() == "Darwin"

    @classmethod
    def linux(cls):
        return cls.os() == "Linux"

    @staticmethod
    def separator():
        return os.sep

    @classmethod
    def command(cls, cmd: str):
        _cmd = cls.COMMAND_DICT.get(cmd, None)

        if not _cmd: raise Exception(f"Command {cmd} not found")

        return _cmd[cls.os()]

    @classmethod
    def execute(
            cls,
            command: Union[str, list[str]],
            shell: Optional[bool] = None,
            capture_output: bool = False,
            check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        安全地执行命令

        Args:
            command: 要执行的命令（字符串或列表）
            shell: 是否使用shell执行（默认：Windows为True，其他为False）
            capture_output: 是否捕获输出
            check: 是否检查命令返回码（非0时抛出异常）

        Returns:
            subprocess.CompletedProcess: 命令执行结果

        Raises:
            subprocess.CalledProcessError: 如果check=True且命令返回非0状态码
        """
        if shell:
            shell = cls.windows()

        return subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            check=check,
            cwd=Path.cwd(),
        )

    @classmethod
    def execute_mapped(
            cls,
            command: str,
            *args: str,
            capture_output: bool = False,
            check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        执行预定义的跨平台命令

        Args:
            command: 预定义命令的键名
            capture_output: 是否捕获输出
            check: 是否检查命令返回码（非0时抛出异常）

        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        cmd = [cls.command(command), [*args]]

        return cls.execute(
            cmd, capture_output=capture_output, check=check
        )

    @classmethod
    def clear(cls):
        cls.execute_mapped("clear")

    @classmethod
    def python_lib(cls, venv_path: Path):
        return venv_path / cls.command("python_venv")

    @classmethod
    def python_venv(cls, venv_path: Path):
        return cls.python_lib(venv_path) / cls.exe("python")

    @classmethod
    def try_execute(cls,
                    command: Union[str, list[str]],
                    args_command: Union[str, list[str]]):
        value = None

        for c in command:
            cmd = [c, *args_command]
            try:
                tp = cls.execute(cmd, shell=True, capture_output=True, check=True)
                value = tp.stdout
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass

        if value is None:
            raise FileNotFoundError

        return value

    @classmethod
    def run_python(cls, args_command: Union[str, list[str]]):
        return cls.try_execute([
            "python",
            "python3",
            "python3.1",
            "python3.2",
            "python3.3",
            "python3.4",
            "python3.5",
            "python3.7",
            "python3.8",
            "python3.9",
            "python3.10",
            "python3.11",
            "python3.12",
            "python3.13",
            "python3.14"
        ], args_command)
