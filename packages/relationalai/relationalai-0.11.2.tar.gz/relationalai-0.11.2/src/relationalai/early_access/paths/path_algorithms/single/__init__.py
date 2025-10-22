import warnings

from relationalai.semantics.reasoners.graph.paths.path_algorithms.single import single_shortest_path, single_walk

__all__ = ["single_shortest_path", "single_walk"]

warnings.warn(
    "relationalai.early_access.paths.path_algorithms.single is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.path_algorithms.single",
    DeprecationWarning,
    stacklevel=2,
)