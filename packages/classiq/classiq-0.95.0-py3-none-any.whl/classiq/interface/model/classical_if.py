import functools
import operator
from collections.abc import Mapping
from typing import TYPE_CHECKING, Literal

import pydantic

from classiq.interface.ast_node import ASTNodeType, reset_lists
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.model.handle_binding import ConcreteHandleBinding, HandleBinding
from classiq.interface.model.quantum_statement import QuantumOperation

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class ClassicalIf(QuantumOperation):
    kind: Literal["ClassicalIf"]

    condition: Expression
    then: "StatementBlock"
    else_: "StatementBlock"
    _condition_wiring_inouts: dict[str, HandleBinding] = pydantic.PrivateAttr(
        default_factory=dict
    )

    def _as_back_ref(self: ASTNodeType) -> ASTNodeType:
        return reset_lists(self, ["then", "else_"])

    @property
    def expressions(self) -> list[Expression]:
        return [self.condition]

    @property
    def blocks(self) -> dict[str, "StatementBlock"]:
        return {"then": self.then, "else_": self.else_}

    @property
    def wiring_inputs(self) -> Mapping[str, HandleBinding]:
        return functools.reduce(
            operator.ior,
            (
                op.wiring_inputs
                for op in (*self.then, *self.else_)
                if isinstance(op, QuantumOperation)
            ),
            dict(),
        )

    @property
    def wiring_inouts(self) -> Mapping[str, ConcreteHandleBinding]:
        return (
            functools.reduce(
                operator.ior,
                (
                    op.wiring_inouts
                    for op in (*self.then, *self.else_)
                    if isinstance(op, QuantumOperation)
                ),
                dict(),
            )
            | self._condition_wiring_inouts
        )

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return functools.reduce(
            operator.ior,
            (
                op.wiring_outputs
                for op in (*self.then, *self.else_)
                if isinstance(op, QuantumOperation)
            ),
            dict(),
        )
