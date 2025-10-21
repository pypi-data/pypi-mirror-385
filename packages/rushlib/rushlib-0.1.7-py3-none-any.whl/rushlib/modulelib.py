import importlib.util
import sys
from pathlib import Path
from typing import Union, Optional

from rushlib.func.injection import FunctionInjection


class ModuleLoader:
    def __init__(self, path: Union[Path, str], name: str, main: str,
                 injection_file: Optional[str] = None, func_injection: dict = None) -> None:
        """
        :param path: 包的位置
        :param name: 主包的名
        :param main: 主文件名
        :param injection_file: 函数注入名
        :param func_injection: 注入的函数或者类
        """

        self.path = path
        self.name = name
        self.main = main
        self.injection_file = injection_file or "func"
        self.func_injection = func_injection or {}

    def __enter__(self):
        spec = importlib.util.spec_from_loader(
            self.name,
            loader=None,
            origin=str(self.path),
            is_package=True
        )
        if spec is None:
            raise ImportError(f"无法创建包规范: {self.name}")

        package_module = importlib.util.module_from_spec(spec)
        sys.modules[self.name] = package_module

        package_module.__path__ = [str(self.path)]
        package_module.__package__ = self.name

        with FunctionInjection(self.path, self.name, self.injection_file,
                               self.func_injection):
            pass

        entry_file = self.path / self.main
        if not entry_file.exists():
            func_module_name = f"{self.name}.func"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[self.name]
            raise FileNotFoundError(f"入口文件 {self.main} 不存在")

        main_module_name = f"{self.name}.main"
        spec = importlib.util.spec_from_file_location(
            main_module_name,
            str(entry_file),
            submodule_search_locations=[str(self.path)],
        )
        if spec is None:
            func_module_name = f"{self.name}.func"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[self.name]
            raise ImportError(f"无法创建模块规范: {entry_file}")

        main_module = importlib.util.module_from_spec(spec)
        sys.modules[main_module_name] = main_module

        try:
            main_module.__package__ = self.name

            spec.loader.exec_module(main_module)
        except Exception as e:
            del sys.modules[main_module_name]
            func_module_name = f"{self.name}.func"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[self.name]
            raise RuntimeError(f"主模块执行失败: {str(e)}")

        return package_module, main_module

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
