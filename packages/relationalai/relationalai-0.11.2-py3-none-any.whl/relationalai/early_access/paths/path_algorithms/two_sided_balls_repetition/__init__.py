import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.two_sided_balls_repetition import two_balls_repetition

__all__ = ['two_balls_repetition']

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.two_sided_balls_repetition is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.two_sided_balls_repetition",
    DeprecationWarning,
    stacklevel=2,
)