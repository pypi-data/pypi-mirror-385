import subprocess
from typing import Optional

from rushlib.system import SystemConsole


def get_python() -> tuple[bool, Optional[str]]:
    try:
        version = SystemConsole.run_python(["--version"])
        return True, version.split(" ")[-1].strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False, None
