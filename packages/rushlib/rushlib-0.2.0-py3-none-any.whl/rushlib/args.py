import argparse

from typing import Optional

def parse_args(tokens: list[str], parser: argparse.ArgumentParser) -> Optional[argparse.Namespace]:
    try:
        return parser.parse_args(tokens)
    except SystemExit:
        return None
    except Exception as e:
        print(f"参数解析错误: {str(e)}")
        return None