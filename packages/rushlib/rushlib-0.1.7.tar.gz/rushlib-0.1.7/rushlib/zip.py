import tempfile
import zipfile
from pathlib import Path


class ZipContent:
    def __init__(self, zip_path: Path | str) -> None:
        """
        初始化上下文管理器
        :param zip_path: 要解压的ZIP文件路径
        """
        self.zip_path = Path(str(zip_path))
        self.temp_dir = None

    def __enter__(self) -> Path:
        """
        进入上下文时执行：
        1. 创建临时目录
        2. 解压ZIP文件到临时目录
        3. 返回临时目录的Path对象
        """
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = Path(self.temp_dir.name)

        # 解压ZIP文件
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            z.extractall(temp_dir_path)

        return temp_dir_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时自动清理临时目录
        """
        if self.temp_dir:
            self.temp_dir.cleanup()
