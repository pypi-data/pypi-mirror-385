from typing import TYPE_CHECKING, Literal

from classiq.interface.ast_node import ASTNodeType, reset_lists
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.model.quantum_statement import QuantumOperation

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class Power(QuantumOperation):
    kind: Literal["Power"]

    power: Expression
    body: "StatementBlock"

    def _as_back_ref(self: ASTNodeType) -> ASTNodeType:
        return reset_lists(self, ["body"])

    @property
    def expressions(self) -> list[Expression]:
        return [self.power]

    @property
    def blocks(self) -> dict[str, "StatementBlock"]:
        return {"body": self.body}
