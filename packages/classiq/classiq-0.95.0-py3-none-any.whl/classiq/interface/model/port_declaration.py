from typing import Any, Literal

import pydantic
from pydantic_core.core_schema import ValidationInfo

from classiq.interface.exceptions import ClassiqInternalError, ClassiqValueError
from classiq.interface.generator.functions.concrete_types import ConcreteQuantumType
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.type_modifier import (
    TypeModifier,
)
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator
from classiq.interface.model.parameter import Parameter
from classiq.interface.model.quantum_type import QuantumBitvector


class AnonPortDeclaration(Parameter):
    quantum_type: ConcreteQuantumType = pydantic.Field(default_factory=QuantumBitvector)
    direction: PortDeclarationDirection
    kind: Literal["PortDeclaration"]
    type_modifier: TypeModifier

    @pydantic.model_validator(mode="before")
    @classmethod
    def _set_kind(cls, values: Any) -> dict[str, Any]:
        return values_with_discriminator(values, "kind", "PortDeclaration")

    @pydantic.field_validator("direction", mode="before")
    @classmethod
    def _direction_validator(
        cls, direction: PortDeclarationDirection, info: ValidationInfo
    ) -> PortDeclarationDirection:
        values = info.data
        if direction is PortDeclarationDirection.Output:
            quantum_type = values.get("quantum_type")
            if quantum_type is None:
                raise ClassiqValueError("Port declaration is missing a type")

        return direction

    def rename(self, new_name: str) -> "PortDeclaration":
        if type(self) not in (AnonPortDeclaration, PortDeclaration):
            raise ClassiqInternalError
        return PortDeclaration(**{**self.__dict__, "name": new_name})

    @property
    def qmod_type_name(self) -> str:
        prefix = ""
        suffix = ""
        if self.type_modifier is TypeModifier.Const:
            prefix += f"{self.type_modifier.name}["
            suffix += "]"
        if self.direction != PortDeclarationDirection.Inout:
            prefix += f"{self.direction.name}["
            suffix += "]"
        return f"{prefix}{self.quantum_type.qmod_type_name}{suffix}"


class PortDeclaration(AnonPortDeclaration):
    name: str
