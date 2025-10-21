from rushlib.func.wrapper import WrapperFunc


def _add(k, a, b):
    return k * (a + b)

@WrapperFunc(_add, 2)
def add(a, b):
    pass


print(add(1, 2))