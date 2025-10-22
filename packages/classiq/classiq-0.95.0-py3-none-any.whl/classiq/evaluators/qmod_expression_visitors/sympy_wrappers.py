from typing import Any

from sympy import Function, Integer
from sympy.logic.boolalg import BooleanFunction


class BitwiseAnd(Function):
    @classmethod
    def eval(cls, a: Any, b: Any) -> int | None:
        if isinstance(a, Integer) and isinstance(b, Integer):
            return a & b

        return None


class BitwiseXor(Function):
    @classmethod
    def eval(cls, a: Any, b: Any) -> int | None:
        if isinstance(a, Integer) and isinstance(b, Integer):
            return a ^ b

        return None


class LogicalXor(BooleanFunction):
    @classmethod
    def eval(cls, a: Any, b: Any) -> bool | None:
        if isinstance(a, bool) and isinstance(b, bool):
            return a ^ b

        return None


class BitwiseOr(Function):
    @classmethod
    def eval(cls, a: Any, b: Any) -> int | None:
        if isinstance(a, Integer) and isinstance(b, Integer):
            return a | b

        return None


class BitwiseNot(Function):
    @classmethod
    def eval(cls, a: Any) -> int | None:
        if isinstance(a, Integer):
            return ~a

        return None


class RShift(Function):
    @classmethod
    def eval(cls, a: Any, b: Any) -> int | None:
        if isinstance(a, Integer) and isinstance(b, Integer):
            return a >> b

        return None


class LShift(Function):
    @classmethod
    def eval(cls, a: Any, b: Any) -> int | None:
        if isinstance(a, Integer) and isinstance(b, Integer):
            return a << b

        return None
