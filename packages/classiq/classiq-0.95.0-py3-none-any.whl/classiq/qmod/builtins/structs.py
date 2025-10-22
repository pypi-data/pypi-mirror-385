from dataclasses import dataclass, fields, is_dataclass
from typing import Union

from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.types.struct_declaration import StructDeclaration
from classiq.interface.helpers.datastructures import LenList
from classiq.interface.helpers.text_utils import are, readable_list, s

from classiq.qmod.builtins.enums import Pauli
from classiq.qmod.cparam import CArray, CInt, CReal
from classiq.qmod.python_classical_type import PythonClassicalType


@dataclass
class PauliTerm:
    """
    A term in a Hamiltonian, represented as a product of single-qubit Pauli matrices.

    Attributes:
        pauli (CArray[Pauli]): The list of the chosen Pauli operators in the term, corresponds to a product of them.
        coefficient (CReal): The coefficient of the term (floating number).
    """

    pauli: CArray[Pauli]
    coefficient: CReal


@dataclass
class IndexedPauli:
    """
    A single-qubit Pauli matrix on a specific qubit given by its index.

    Attributes:
        pauli (Pauli): The Pauli operator.
        index (CInt): The index of the qubit being operated on.
    """

    pauli: Pauli
    index: CInt


@dataclass
class SparsePauliTerm:
    """
    A term in the Hamiltonian, represented as a sparse product of single-qubit Pauli
    matrices.

       Attributes:
           paulis (CArray[IndexedPauli]): The list of chosen sparse Pauli operators in the term corresponds to a product of them. (See IndexedPauli)
           coefficient (CReal): The coefficient of the term (floating number).
    """

    paulis: CArray[IndexedPauli]
    coefficient: CReal


@dataclass
class SparsePauliOp:
    """
    Represents a collection of sparse Pauli operators.

    Attributes:
        terms (CArray[SparsePauliTerm]): The list of chosen sparse Pauli terms, corresponds to a product of them. (See: SparsePauliTerm)
        num_qubits (CInt): The number of qubits in the Hamiltonian.
    """

    terms: list[SparsePauliTerm]
    num_qubits: int

    def __mul__(self, obj: Union[float, "SparsePauliOp"]) -> "SparsePauliOp":
        if isinstance(obj, (int, float, complex)):
            return SparsePauliOp(
                terms=LenList(
                    [
                        SparsePauliTerm(
                            paulis=term.paulis,
                            coefficient=obj * term.coefficient,  # type:ignore[arg-type]
                        )
                        for term in self.terms
                    ]
                ),
                num_qubits=self.num_qubits,
            )
        if len(self.terms) != 1 or len(obj.terms) != 1:
            raise ClassiqValueError("Cannot attach a pauli to multiple pauli terms")
        existing_indices = {
            indexed_pauli.index
            for indexed_pauli in self.terms[0].paulis  # type:ignore[attr-defined]
        }
        added_indices = {
            indexed_pauli.index
            for indexed_pauli in obj.terms[0].paulis  # type:ignore[attr-defined]
        }
        overlapping_indices = sorted(existing_indices.intersection(added_indices))
        if len(overlapping_indices):
            raise ClassiqValueError(
                f"Pauli{s(overlapping_indices)} at "
                f"{'indices' if len(overlapping_indices) > 1 else 'index'} "
                f"{readable_list(overlapping_indices)} {are(overlapping_indices)} "
                f"already assigned"
            )
        return SparsePauliOp(
            terms=LenList(
                [
                    SparsePauliTerm(
                        paulis=LenList(  # type:ignore[call-overload]
                            self.terms[0].paulis + obj.terms[0].paulis
                        ),
                        coefficient=self.terms[0].coefficient
                        * obj.terms[0].coefficient,  # type:ignore[arg-type]
                    )
                ]
            ),
            num_qubits=max(self.num_qubits, obj.num_qubits),
        )

    def __rmul__(self, obj: Union[float, "SparsePauliOp"]) -> "SparsePauliOp":
        return self.__mul__(obj)

    def __add__(self, other: "SparsePauliOp") -> "SparsePauliOp":
        return SparsePauliOp(
            terms=LenList(self.terms + other.terms),
            num_qubits=max(self.num_qubits, other.num_qubits),
        )

    def __sub__(self, other: "SparsePauliOp") -> "SparsePauliOp":
        return self + -1.0 * other

    def __str__(self) -> str:
        return " + ".join(
            (f"{term.coefficient}*" if term.coefficient != 1 else "")
            + "*".join(
                f"Pauli.{indexed_pauli.pauli.name}({indexed_pauli.index})"
                for indexed_pauli in term.paulis  # type:ignore[attr-defined]
            )
            for term in self.terms
        )


@dataclass
class CombinatorialOptimizationSolution:
    probability: CReal
    cost: CReal
    solution: CArray[CInt]
    count: CInt


@dataclass
class GaussianModel:
    num_qubits: CInt
    normal_max_value: CReal
    default_probabilities: CArray[CReal]
    rhos: CArray[CReal]
    loss: CArray[CInt]
    min_loss: CInt


@dataclass
class LogNormalModel:
    num_qubits: CInt
    mu: CReal
    sigma: CReal


BUILTIN_STRUCT_DECLARATIONS = {
    struct_decl.__name__: StructDeclaration(
        name=struct_decl.__name__,
        variables={
            field.name: PythonClassicalType().convert(field.type, nested=True)
            for field in fields(struct_decl)
        },
    )
    for struct_decl in vars().values()
    if is_dataclass(struct_decl)
}


__all__ = [
    "CombinatorialOptimizationSolution",
    "GaussianModel",
    "IndexedPauli",
    "LogNormalModel",
    "PauliTerm",
    "SparsePauliOp",
    "SparsePauliTerm",
]
