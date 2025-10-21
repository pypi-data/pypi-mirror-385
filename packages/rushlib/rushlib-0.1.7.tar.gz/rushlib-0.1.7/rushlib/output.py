from colorama import Style

from rushlib.color import MColor, Red


def print_color(color: MColor,
                *values,
                sep: str | None = " ",
                end: str | None = "\n",
                file=None,
                flush=False):
    print(f"{color}", end="")
    print(*values, sep=sep, end=end, file=file, flush=flush)
    print(f"{Style.RESET_ALL}", end="")

def print_red(
        *values,
        sep: str | None = " ",
        end: str | None = "\n",
        file=None,
        flush=False):
    print_color(Red(), *values, sep=sep, end=end, file=file, flush=flush)