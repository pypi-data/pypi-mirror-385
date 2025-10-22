from typing import TYPE_CHECKING, Literal

import pydantic

from classiq.interface.model.quantum_statement import QuantumOperation

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class Block(QuantumOperation):
    kind: Literal["Block"]

    statements: "StatementBlock"

    label: str | None = pydantic.Field(default=None)

    @property
    def blocks(self) -> dict[str, "StatementBlock"]:
        return {"statements": self.statements}
