import importlib.util
import sys
from typing import Optional, Callable

from rushlib.types import path_type


class FunctionInjection:
    def __init__(self, path: path_type, package_name: str, func_name: str = None,
                 func_replacements: Optional[dict[str, Callable]] = None):
        self.package_path = path
        self.func_name = func_name or "func"
        self.package_name = package_name
        self.func_replacements = func_replacements or {}

        self.func_module = None

    def __enter__(self):
        func_file = self.package_path / f"{self.func_name}.py"
        if func_file.exists():
            func_module_name = f"{self.package_name}.{self.func_name}"
            func_spec = importlib.util.spec_from_file_location(
                func_module_name,
                str(func_file),
                submodule_search_locations=[str(self.package_path)],
            )
            if func_spec is None:
                del sys.modules[self.package_name]
                raise ImportError(f"无法创建func模块规范: {func_file}")

            # 创建func模块
            self.func_module = importlib.util.module_from_spec(func_spec)
            sys.modules[func_module_name] = self.func_module

            # 设置func模块的包信息
            self.func_module.__package__ = self.package_name

            try:
                # 执行func模块
                func_spec.loader.exec_module(self.func_module)

                # 替换func模块中的函数
                for func_name, replacement in self.func_replacements.items():
                    setattr(self.func_module, func_name, replacement)
            except Exception as e:
                # 清理
                del sys.modules[func_module_name]
                del sys.modules[self.package_name]
                raise RuntimeError(f"func模块执行失败: {str(e)}")

        return self.func_module

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
