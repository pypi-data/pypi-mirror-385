import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.find_paths import find_shortest_paths, find_walks

__all__ = ["find_shortest_paths", "find_walks"]

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.find_paths is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.find_paths",
    DeprecationWarning,
    stacklevel=2,
)