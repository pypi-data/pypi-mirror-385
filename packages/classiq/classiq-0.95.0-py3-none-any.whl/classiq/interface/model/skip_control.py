from typing import TYPE_CHECKING, Literal

from classiq.interface.model.quantum_statement import QuantumOperation

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class SkipControl(QuantumOperation):
    kind: Literal["SkipControl"]
    body: "StatementBlock"

    @property
    def blocks(self) -> dict[str, "StatementBlock"]:
        return {"body": self.body}
