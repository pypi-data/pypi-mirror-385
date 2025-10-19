from dataclasses import dataclass, field


@dataclass(slots=True)
class Size:
    width: int
    height: int

    def _binary_operator(self, other, op_func):
        """通用的二元运算符模板"""
        if isinstance(other, Size):
            return Size(op_func(self.width, other.width), op_func(self.height, other.height))
        elif isinstance(other, (int, float)):
            return Size(op_func(self.width, other), op_func(self.height, other))
        elif isinstance(other, tuple) and len(other) == 2:
            return Size(op_func(self.width, other[0]), op_func(self.height, other[1]))
        else:
            raise ValueError("Operand must be Size, number, or 2-element tuple")

    def __add__(self, other):
        return self._binary_operator(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self._binary_operator(other, lambda x, y: x - y)

    def __mul__(self, other):
        return self._binary_operator(other, lambda x, y: x * y)

    def __truediv__(self, other):
        return self._binary_operator(other, lambda x, y: x / y)

    def __iter__(self):
        yield self.width
        yield self.height
