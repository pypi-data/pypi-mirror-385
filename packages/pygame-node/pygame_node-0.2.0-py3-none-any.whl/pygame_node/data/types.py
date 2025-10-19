
from typing import Tuple, Callable


class Color:
    def __init__(self, *args, **kwargs) -> None:
        """
        创建颜色类型, Color(红, 绿, 蓝, 不透明度)
        示例:
        >>> Color((255, 255, 255, 0.7))
        Color(255, 255, 255, 0.7)
        >>> Color(255, 255, 255, 0.2)
        Color(255, 255, 255, 0.2)
        >>> Color("0xffffff")
        Color(255, 255, 255, 0.0)
        >>> Color("0xfff")
        Color(255, 255, 255, 0.0)
        >>> Color(Color(255, 255, 255, 0.5))
        Color(255, 255, 255, 0.5)

        :param args:
        :param kwargs:
        """
        if len(args) == 1 and len(args) > 2:
            if isinstance(args[0], Color):
                self._r, self._g, self._b, self._a = args[0].r, args[0].g, args[0].b, args[0].a
            elif isinstance(args[0], Tuple):
                self._r, self._g, self._b = args[0][0:3]
                self._a = args[0][3] if len(args[0]) == 4 else 1.0
            elif isinstance(args[0], str) and args[0].startswith("0x"):
                _hex: str = args[0][2:]
                if len(_hex) == 3:
                    self._r, self._g, self._b = int(_hex[0] + _hex[0], 16), int(_hex[1] + _hex[1], 16), int(_hex[2] + _hex[2], 16)
                elif len(_hex) == 6:
                    self._r, self._g, self._b = int(_hex[0:2], 16), int(_hex[2:4], 16), int(_hex[4:6], 16)
                self._a = 1.0
        elif len(args) == 3:
            self._r, self._g, self._b = args
            self._a = 1.0
        elif len(args) == 4:
            self._r, self._g, self._b, self._a = args
        else:
            raise TypeError

    @property
    def r(self):
        return min(self._r, 255)

    @r.setter
    def r(self, r):
        self._r = r

    @property
    def g(self):
        return min(self._g, 255)

    @g.setter
    def g(self, g):
        self._g = g

    @property
    def b(self):
        return min(self._b, 255)

    @b.setter
    def b(self, b):
        self._b = b

    @property
    def a(self):
        return min(self._a, 1.0)

    @a.setter
    def a(self, a):
        self._a = a

    @property
    def rgb(self):
        return self.r, self.g, self.b

    @property
    def rgba(self):
        return self.r, self.g, self.b, int(self.a * 255)

    def __eq__(self, other):
        if self is other: return True
        elif isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.r}, {self.g}, {self.b}, {self.a})"

    def __deepcopy__(self, memo):
        new = self.__class__.__new__(self.__class__)
        memo[id(self)] = new
        new._r = self._r
        new._g = self._g
        new._b = self._b
        new._a = self._a
        return new

    def _binary_operator(self, other, op_func: Callable[[int | float], int | float]):
        """通用的二元运算符模板"""
        if isinstance(other, Color):
            return Color(op_func(self.r, other.r), op_func(self.g, other.g), op_func(self.b, other.b), op_func(self.a, other.a))
        elif isinstance(other, (int, float)):
            return Color(op_func(self.r, other), op_func(self.g, other), op_func(self.b, other), op_func(self.a, other))
        elif isinstance(other, (tuple, list)) and len(other) == 4:
            return Color(op_func(self.r, other[0]), op_func(self.g, other[1]), op_func(self.b, other[2]), op_func(self.a, other[3]))
        else:
            raise ValueError("Operand must be Color, number, or 4-element tuple")

    def __mul__(self, other):
        return self._binary_operator(other, lambda x, y: x * y)

    def __truediv__(self, other):
        return self._binary_operator(other, lambda x, y: x / y)

    def __sub__(self, other):
        return self._binary_operator(other, lambda x, y: x - y)

    def __add__(self, other):
        return self._binary_operator(other, lambda x, y: x + y)

    __str__ = __repr__

