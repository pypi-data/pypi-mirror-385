from typing import Final

from classiq.interface.applications.iqae.iqae_result import IQAEResult
from classiq.interface.exceptions import ClassiqError
from classiq.interface.executor.execution_preferences import QaeWithQpeEstimationMethod
from classiq.interface.executor.quantum_program_params import ExecutionParams
from classiq.interface.executor.result import (
    EstimationResult,
    EstimationResults,
    ExecutionDetails,
    MultipleExecutionDetails,
)
from classiq.interface.executor.vqe_result import VQESolverResult
from classiq.interface.generator.functions.qmod_python_interface import QmodPyStruct

from classiq.qmod.builtins.enums import Optimizer

_CALL_IN_QFUNC_ERROR = (
    'Cannot call "{}" in a quantum context. "{}" is a classical execution primitive.'
)

CARRAY_SEPARATOR: Final[str] = "_"


def _raise_error(primitive_name: str) -> None:
    raise ClassiqError(_CALL_IN_QFUNC_ERROR.format(primitive_name, primitive_name))


def save(values_to_save: dict) -> None:
    _raise_error("save")


def sample(  # type: ignore[return]
    execution_params: ExecutionParams | None = None,
) -> ExecutionDetails:
    _raise_error("sample")


def batch_sample(  # type: ignore[return]
    batch_execution_params: list[ExecutionParams],
) -> MultipleExecutionDetails:
    _raise_error("batch_sample")


def estimate(  # type: ignore[return]
    hamiltonian: list[QmodPyStruct], execution_params: ExecutionParams | None = None
) -> EstimationResult:
    _raise_error("estimate")


def batch_estimate(  # type: ignore[return]
    hamiltonian: list[QmodPyStruct],
    batch_execution_params: list[ExecutionParams],
) -> EstimationResults:
    _raise_error("batch_estimate")


def vqe(  # type: ignore[return]
    hamiltonian: list[QmodPyStruct],
    maximize: bool,
    initial_point: list[float],
    optimizer: Optimizer,
    max_iteration: int,
    tolerance: float,
    step_size: float,
    skip_compute_variance: bool,
    alpha_cvar: float,
) -> VQESolverResult:
    _raise_error("vqe")


def qae_with_qpe_result_post_processing(  # type: ignore[return]
    estimation_register_size: int,
    estimation_method: QaeWithQpeEstimationMethod,
    result: ExecutionDetails,
) -> float:
    _raise_error("qae_with_qpe_result_post_processing")


def iqae(  # type: ignore[return]
    epsilon: float,
    alpha: float,
    execution_params: ExecutionParams | None = None,
) -> IQAEResult:
    _raise_error("iqae")


__all__ = [
    "batch_estimate",
    "batch_sample",
    "estimate",
    "iqae",
    "qae_with_qpe_result_post_processing",
    "sample",
    "save",
    "vqe",
]


def __dir__() -> list[str]:
    return __all__
