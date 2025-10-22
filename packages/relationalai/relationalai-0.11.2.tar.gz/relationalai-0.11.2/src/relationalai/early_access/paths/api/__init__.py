import warnings

from relationalai.semantics.reasoners.graph.paths.api import path, star, match, node, union, node_filter

__all__ = ["path", "star", "match", "node", "union", "node_filter"]

warnings.warn(
    "relationalai.early_access.paths.api is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.api",
    DeprecationWarning,
    stacklevel=2,
)