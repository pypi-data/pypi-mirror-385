from colorama import Style

from rushlib.color import MColor, White, Red, Yellow


class Text:
    def __init__(self, text="", color: MColor = White()):
        self._text = text
        self._color = color

    def sub_string(self, start: int, end: int) -> str:
        return self.text[start:end]

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    def __add__(self, other):
        if isinstance(other, Text):
            return Text(self.text + other.text, self.color)

        if isinstance(other, str):
            return Text(self.text + other, self.color)

        raise TypeError(other)

    def __len__(self):
        return len(self.text)

    def __getitem__(self, item):
        return self.text[item]

    def __iter__(self):
        return self.text.__iter__()

    def __str__(self):
        return f'{self.color}{self.text}{Style.RESET_ALL}'


class Error(Text):
    def __init__(self, text):
        super().__init__(text, Red())


class Info(Text):
    def __init__(self, text):
        super().__init__(text, White())


class Warn(Text):
    def __init__(self, text):
        super().__init__(text, Yellow())
