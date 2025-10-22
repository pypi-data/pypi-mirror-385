import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.two_sided_balls_upto import two_balls_upto

__all__ = ['two_balls_upto']

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.two_sided_balls_upto is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.two_sided_balls_upto",
    DeprecationWarning,
    stacklevel=2,
)