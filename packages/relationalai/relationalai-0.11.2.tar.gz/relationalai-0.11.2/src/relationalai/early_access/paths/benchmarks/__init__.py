# __init__.py for rpq module
import warnings

from relationalai.semantics.reasoners.graph.paths.benchmarks.grid_graph import create_labeled_grid

__all__ = ["create_labeled_grid"]

warnings.warn(
    "relationalai.early_access.paths.benchmarks is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.benchmarks",
    DeprecationWarning,
    stacklevel=2,
)
