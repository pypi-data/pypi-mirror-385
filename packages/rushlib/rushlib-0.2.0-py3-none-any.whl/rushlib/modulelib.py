import dataclasses
import importlib.util
import sys

from rushlib.func.injection import FunctionInjection
from rushlib.types import path_type


def include(src: path_type):
    sys.path.insert(0, str(src))


@dataclasses.dataclass
class ModuleInfo:
    name: str = None
    funcs: dict = None


class ModuleLoader:
    def __init__(self, root: path_type, pack: ModuleInfo, main: str, func: ModuleInfo) -> None:
        """
        :param root: 包的位置
        """

        self.root = root
        self.pack = pack
        self.main = main
        self.func = func

    def __enter__(self):
        name = self.pack.name
        func = self.func.name or "func"
        funcs = self.func.funcs or {}

        spec = importlib.util.spec_from_loader(
            name,
            loader=None,
            origin=str(self.root),
            is_package=True
        )
        if spec is None:
            raise ImportError(f"无法创建包规范: {name}")

        package_module = importlib.util.module_from_spec(spec)
        sys.modules[name] = package_module

        package_module.__path__ = [str(self.root)]
        package_module.__package__ = name

        with FunctionInjection(self.root, name, func, funcs):
            pass

        entry_file = self.root / self.main
        if not entry_file.exists():
            func_module_name = f"{name}.{func}"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[name]
            raise FileNotFoundError(f"入口文件 {self.main} 不存在")

        main_module_name = f"{name}.{self.main}"
        spec = importlib.util.spec_from_file_location(
            main_module_name,
            str(entry_file),
            submodule_search_locations=[str(self.root)],
        )
        if spec is None:
            func_module_name = f"{name}.{func}"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[name]
            raise ImportError(f"无法创建模块规范: {entry_file}")

        main_module = importlib.util.module_from_spec(spec)
        sys.modules[main_module_name] = main_module

        try:
            main_module.__package__ = name

            spec.loader.exec_module(main_module)
        except Exception as e:
            del sys.modules[main_module_name]
            func_module_name = f"{name}.{func}"
            if func_module_name in sys.modules:
                del sys.modules[func_module_name]
            del sys.modules[name]
            raise RuntimeError(f"主模块执行失败: {str(e)}")

        return package_module, main_module

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
