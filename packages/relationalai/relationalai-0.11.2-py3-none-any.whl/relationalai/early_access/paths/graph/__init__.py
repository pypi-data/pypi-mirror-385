import warnings

from relationalai.semantics.reasoners.graph.paths.graph import Graph

__all__ = ["Graph"]

warnings.warn(
    "relationalai.early_access.paths.graph is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph",
    DeprecationWarning,
    stacklevel=2,
)