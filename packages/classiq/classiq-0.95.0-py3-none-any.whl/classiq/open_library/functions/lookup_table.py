from itertools import product

from classiq.interface.exceptions import ClassiqValueError

from classiq.qmod.builtins.operations import assign, bind, within_apply
from classiq.qmod.qmod_variable import QNum
from classiq.qmod.symbolic import subscript
from classiq.qmod.utilities import RealFunction, get_temp_var_name, qnum_values


def _get_qnum_values(num: QNum) -> list[float]:
    size = num.size
    is_signed = num.is_signed
    fraction_digits = num.fraction_digits
    if (
        not isinstance(size, int)
        or not isinstance(is_signed, bool)
        or not isinstance(fraction_digits, int)
    ):
        raise ClassiqValueError(f"QNum argument {str(num)!r} has symbolic attributes")

    return qnum_values(size, is_signed, fraction_digits)


def get_lookup_table(func: RealFunction, *targets: QNum) -> list[float]:
    """
    Reduces a classical function into a lookup table over all the possible values
    of the quantum numbers.

    Args:
        func: A Python function
        *targets: One or more initialized quantum numbers

    Returns:
        The function's lookup table

    Notes:
        The QNum arguments must have generative attributes
    """
    target_vals = [_get_qnum_values(target) for target in targets]
    return [func(*vals[::-1]) for vals in product(*target_vals[::-1])]


def span_lookup_table(func: RealFunction, *targets: QNum) -> QNum:
    """
    Applies a classical function to quantum numbers.

    Works by reducing the function into a lookup table over all the possible values
    of the quantum numbers.

    Args:
        func: A Python function
        *targets: One or more initialized quantum numbers

    Returns:
        The quantum result of applying func to targets

    Notes:
        The QNum arguments must have generative attributes
    """
    lookup_table = get_lookup_table(func, *targets)

    index_size = sum(target.size for target in targets)
    index: QNum = QNum(get_temp_var_name(), size=index_size)
    result: QNum = QNum(get_temp_var_name("result"))

    within_apply(
        lambda: bind(list(targets), index),
        lambda: assign(subscript(lookup_table, index), result),
    )
    return result
