import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.one_sided_ball_upto import ball_upto

__all__ = ["ball_upto"]

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.one_sided_ball_upto is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.one_sided_ball_upto",
    DeprecationWarning,
    stacklevel=2,
)