import os
import sys
from pathlib import Path

from rushlib.types import path_type


class MPath:
    @staticmethod
    def to_path(path: path_type) -> Path:
        return Path(str(path))

    @staticmethod
    def get_exe_dir():
        """获取当前 EXE 文件所在的目录路径"""
        # 如果是打包后的环境
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            return Path(os.path.dirname(exe_path))
        else:
            return Path(os.path.dirname(os.path.abspath(sys.argv[0])))

    @staticmethod
    def get() -> Path:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath("")

        return Path(base_path)
