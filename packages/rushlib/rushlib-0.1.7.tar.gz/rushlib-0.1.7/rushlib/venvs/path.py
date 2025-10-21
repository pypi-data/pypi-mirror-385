from pathlib import Path

from rushlib.system import SystemConsole


def venv_path(venv: str = ".venv") -> Path:
    python = SystemConsole.python_venv(Path.cwd() / venv)

    if python.exists():
        return python

    return Path(SystemConsole.run_python(["-c", "import sys; print(sys.executable)"])[1])
