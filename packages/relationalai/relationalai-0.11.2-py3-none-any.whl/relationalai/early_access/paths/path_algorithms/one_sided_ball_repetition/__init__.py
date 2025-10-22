import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.one_sided_ball_repetition import ball_with_repetition

__all__ = ["ball_with_repetition"]

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.one_sided_ball_repetition is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.one_sided_ball_repetition",
    DeprecationWarning,
    stacklevel=2,
)