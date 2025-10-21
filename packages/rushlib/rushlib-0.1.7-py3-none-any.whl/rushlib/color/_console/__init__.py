from colorama import Fore


class ConsoleColor:
    def __init__(self, fore):
        self._fore = fore

    @property
    def fore(self):
        return self._fore

    def __str__(self):
        return self.fore


class ForeBlack(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.BLACK)


class ForeRed(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.RED)


class ForeGreen(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.GREEN)


class ForeYellow(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.YELLOW)


class ForeBlue(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.BLUE)


class ForeMagenta(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.MAGENTA)


class ForeCyan(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.CYAN)


class ForeWhite(ConsoleColor):
    def __init__(self):
        super().__init__(Fore.WHITE)
