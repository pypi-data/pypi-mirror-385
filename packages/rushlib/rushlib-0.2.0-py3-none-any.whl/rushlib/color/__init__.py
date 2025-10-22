from rushlib.color._console import *
from rushlib.color.util import *


class MColor:
    CONSOLE_COLOR = ForeWhite()

    def __init__(self, r: int = 255, g: int = 255, b: int = 255, a: int = 255):
        """
        增强版的Color, 支持rgb转hex, 可以直接作为pygame的Color
        :param r: R
        :param g: G
        :param b: B
        :param a: A
        """
        self._r, self._g, self._b, self._a = self.vali_rgba(r, g, b, a)

    @staticmethod
    def from_hex(hex_str: str = "#FFFFFF"):
        """
        将16进制颜色代码转为MColor
        :param hex_str: 16进制string
        :return: new MColor
        """
        r, g, b, a = hex_to_rgb(hex_str)
        return MColor(r, g, b, a)

    @staticmethod
    def vali_rgba(r, g, b, a=255):
        return vali_rgba(r, g, b, a)

    @property
    def r(self) -> int:
        return self._r

    @r.setter
    def r(self, value: int) -> None:
        if 0 < value <= 255:
            self._r = value

        self.r = 255

    @property
    def float_r(self) -> float:
        return self.r / 255.0

    @property
    def g(self) -> int:
        return self._g

    @g.setter
    def g(self, value: int) -> None:
        if 0 < value <= 255:
            self._g = value
            return

        self.g = 255

    @property
    def float_g(self) -> float:
        return self.g / 255.0

    @property
    def b(self) -> int:
        return self._b

    @b.setter
    def b(self, value: int) -> None:
        if 0 < value <= 255:
            self._b = value
            return

        self.b = 255

    @property
    def float_b(self) -> float:
        return self.b / 255.0

    @property
    def a(self) -> int:
        return self._a

    @a.setter
    def a(self, value: int) -> None:
        if 0 < value <= 255:
            self._a = value
            return

        self.a = 255

    @property
    def float_a(self) -> float:
        return self.a / 255.0

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b

    @property
    def float_rgb(self) -> tuple[float, float, float]:
        return self.float_r, self.float_g, self.float_b

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        return self.rgb[0], self.rgb[1], self.rgb[2], self.a

    @property
    def float_rgba(self) -> tuple[float, float, float, float]:
        return self.float_rgb[0], self.float_rgb[1], self.float_rgb[2], self.float_a

    @property
    def hex(self) -> str:
        return rgb_to_hex(self.r, self.g, self.b)

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

    def __len__(self):
        return 4

    def __getitem__(self, item):
        prop = self.r, self.g, self.b, self.a

        return prop[item]

    def __add__(self, other):
        if isinstance(other, MColor):
            r, g, b, a = other
            return MColor(self.r + r, self.g + g, self.b + b, self.a + a)

        raise TypeError(other)

    def __sub__(self, other):
        if isinstance(other, MColor):
            r, g, b, a = other
            return MColor(self.r - r, self.g - g, self.b - b, self.a - a)

        raise TypeError(other)

    def __repr__(self):
        return f"[MColor r={self.r} g={self.g} b={self.b} a={self.a}]"

    def __str__(self):
        return f'{self.CONSOLE_COLOR}'


class Black(MColor):
    CONSOLE_COLOR = ForeBlack()

    def __init__(self, a: int = 255):
        super().__init__(0, 0, 0, a)


class Red(MColor):
    CONSOLE_COLOR = ForeRed()

    def __init__(self, a: int = 255):
        super().__init__(255, 0, 0, a)


class Green(MColor):
    CONSOLE_COLOR = ForeGreen()

    def __init__(self, a: int = 255):
        super().__init__(0, 255, 0, a)


class Yellow(MColor):
    CONSOLE_COLOR = ForeYellow()

    def __init__(self, a: int = 255):
        super().__init__(255, 255, 0, a)


class Blue(MColor):
    CONSOLE_COLOR = ForeBlue()

    def __init__(self, a: int = 255):
        super().__init__(0, 0, 255, a)


class Magenta(MColor):
    CONSOLE_COLOR = ForeMagenta()

    def __init__(self, a: int = 255):
        super().__init__(255, 0, 255, a)


class Cyan(MColor):
    CONSOLE_COLOR = ForeCyan()

    def __init__(self, a: int = 255):
        super().__init__(0, 255, 255, a)


class White(MColor):
    CONSOLE_COLOR = ForeWhite()

    def __init__(self, a: int = 255):
        super().__init__(255, 255, 255, a)
