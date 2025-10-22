import warnings

from relationalai.semantics.reasoners.graph.paths.utilities.iterators import setup_iteration

__all__ = ["setup_iteration"]

warnings.warn(
    "relationalai.early_access.paths.utilities.iterators is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.utilities.iterators",
    DeprecationWarning,
    stacklevel=2,
)