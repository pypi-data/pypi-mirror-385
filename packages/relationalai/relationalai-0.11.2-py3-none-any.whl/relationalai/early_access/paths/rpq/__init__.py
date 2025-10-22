# __init__.py for rpq module
import warnings

from relationalai.semantics.reasoners.graph.paths.rpq import RPQ, Node, Edge, Concat, Union, Star

__all__ = ["RPQ", "Node", "Edge", "Concat", "Union", "Star"]

warnings.warn(
    "relationalai.early_access.paths.rpq is deprecated. "
    "Please migrate to relationalai.semantics.reasoners.graph.paths.rpq",
    DeprecationWarning,
    stacklevel=2,
)
