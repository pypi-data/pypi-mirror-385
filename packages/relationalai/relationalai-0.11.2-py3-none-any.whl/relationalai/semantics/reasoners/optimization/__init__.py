__version__ = "0.0.0"

# NOTE(coey) using Solver class from old solvers library to avoid code duplication
from relationalai.experimental.solvers import Solver, Provider

from .common import make_name, all_different, implies
from .solvers_pb import SolverModelPB
from .solvers_dev import SolverModelDev

def SolverModel(model, num_type: str, use_pb: bool = True):
    if use_pb:
        return SolverModelPB(model, num_type)
    else:
        return SolverModelDev(model, num_type)

__all__ = [
    "Solver",
    "Provider",
    "SolverModel",
    "make_name",
    "all_different",
    "implies",
]
