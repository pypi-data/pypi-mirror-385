from classiq.qmod.qfunc import qperm
from classiq.qmod.qmod_variable import Const, QArray, QBit


@qperm(external=True)
def MCX(ctrl: Const[QArray[QBit]], target: QBit) -> None:
    pass
