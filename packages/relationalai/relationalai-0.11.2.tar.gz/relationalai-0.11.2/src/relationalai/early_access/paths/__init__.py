## pathfinder module
import warnings

from relationalai.semantics.reasoners.graph.paths.api import node, edge, path, optional, plus, star, union, match

__all__ = [
    'node',
    'edge',
    'path',
    'optional',
    'plus',
    'star',
    'union',
    'match',
]

warnings.warn(
    "relationalai.early_access.paths.* is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.*",
    DeprecationWarning,
    stacklevel=2,
)
