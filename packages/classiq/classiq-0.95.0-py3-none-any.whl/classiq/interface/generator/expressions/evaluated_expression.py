import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, get_args

from sympy import Expr

from classiq.interface.backend.pydantic_backend import EXECUTION_PARAMETER_PATTERN
from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.expressions.expression_types import (
    ExpressionValue,
    RuntimeConstant,
)
from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)


@dataclass(frozen=True)
class EvaluatedExpression:
    value: ExpressionValue

    def is_constant(self, constant_type: type | None = None) -> bool:
        return isinstance(
            self.value,
            get_args(RuntimeConstant) if constant_type is None else constant_type,
        )

    def as_constant_type(self, constant_type: type) -> Any:
        if not self.is_constant():
            raise ClassiqValueError(
                f"Invalid access to expression {self.value!r} as {constant_type}"
            )

        return constant_type(self.value)

    def to_int_value(self) -> int:
        return self.as_constant_type(int)

    def to_bool_value(self) -> bool:
        return self.as_constant_type(bool)

    def to_float_value(self) -> float:
        return self.as_constant_type(float)

    def to_list(self) -> list:
        return self.as_constant_type(list)

    def to_struct_dict(self) -> Mapping[str, Any]:
        if not isinstance(self.value, QmodStructInstance):
            raise ClassiqValueError(
                f"Invalid access to expression {self.value} as SympyStructInstance"
            )

        return self.value.fields

    def as_expression(self) -> str:
        if self.value is None:
            raise ClassiqValueError("Invalid access to unevaluated expression")

        return str(self.value)

    def is_identifier(self) -> bool:
        return (
            isinstance(self.value, Expr)
            and re.fullmatch(EXECUTION_PARAMETER_PATTERN, str(self.value)) is not None
        )
