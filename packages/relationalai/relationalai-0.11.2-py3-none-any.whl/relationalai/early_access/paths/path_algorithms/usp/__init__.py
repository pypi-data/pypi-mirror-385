import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.usp import compute_usp, compute_nsp

__all__ = ["compute_usp", "compute_nsp"]

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.usp is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.usp",
    DeprecationWarning,
    stacklevel=2,
)