import inspect
from inspect import Parameter
from functools import wraps
from typing import Callable, Any


def smart_call(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    智能调用函数，根据目标函数的参数签名自动匹配传入的参数

    :param func: 要调用的目标函数
    :param *args: 位置参数
    :param **kwargs: 关键字参数

    :return: 目标函数的执行结果
    """
    try:
        # 获取函数签名
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        # 无法获取签名时直接尝试调用
        return func(*args, **kwargs)

    # 准备参数绑定
    bound_args = {}
    params = sig.parameters

    # 处理位置参数
    args_iter = iter(args)
    for name, param in params.items():
        if param.kind in (Parameter.POSITIONAL_ONLY,
                          Parameter.POSITIONAL_OR_KEYWORD,
                          Parameter.KEYWORD_ONLY):
            # 尝试从位置参数获取值
            if args_iter:
                try:
                    bound_args[name] = next(args_iter)
                    continue
                except StopIteration:
                    pass

            # 如果位置参数用完，尝试从关键字参数获取
            if name in kwargs:
                bound_args[name] = kwargs[name]
            elif param.default is not Parameter.empty:
                # 使用默认值
                bound_args[name] = param.default
            else:
                # 必需参数缺失
                raise TypeError(f"Missing required argument: {name}")

        elif param.kind == Parameter.VAR_POSITIONAL:
            # 处理 *args 参数
            bound_args[name] = tuple(args_iter)
            args_iter = None  # 标记位置参数已耗尽

    # 处理剩余的关键字参数
    for name, param in params.items():
        if param.kind == Parameter.VAR_KEYWORD:
            # 处理 **kwargs 参数
            bound_args[name] = {
                k: v for k, v in kwargs.items()
                if k not in bound_args
            }
            break
        elif name not in bound_args and param.kind == Parameter.KEYWORD_ONLY:
            # 处理仅关键字参数
            if name in kwargs:
                bound_args[name] = kwargs[name]
            elif param.default is not Parameter.empty:
                bound_args[name] = param.default
            else:
                raise TypeError(f"Missing required keyword argument: {name}")

    return func(**bound_args)


def adapt_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return smart_call(func, *args, **kwargs)

    return wrapper