class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, item):
        return self.__dict__[item]

    def __len__(self):
        return 2

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return Vector2(self.x / other.x, self.y / other.y)

    def __str__(self):
        return f'{self.x}, {self.y}'


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, item):
        return self.__dict__[item]

    def __len__(self):
        return 3

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __truediv__(self, other):
        return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)

    def __str__(self):
        return f'{self.x}, {self.y}, {self.z}'


class Vector4:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __getitem__(self, item):
        return self.__dict__[item]

    def __len__(self):
        return 4

    def __add__(self, other):
        return Vector4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        return Vector4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __mul__(self, other):
        return Vector4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)

    def __truediv__(self, other):
        return Vector4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)

    def __str__(self):
        return f'{self.x}, {self.y}, {self.z}, {self.w}'


vec2 = Vector2
vec3 = Vector3
vec4 = Vector4
