"""
Core functionality for the graphs package.
"""

import warnings

from decimal import Decimal
from functools import cached_property
from numbers import Number, Real
from typing import Optional, Type, Union

import gravis
import numpy

from relationalai.semantics import (
    Model, Concept, Relationship,
    Error, Integer, Float,
    where, define, union, not_, select,
    min, max, rank, desc,
    count, sum, avg,
)
from relationalai.docutils import include_in_docs
from relationalai.semantics.std.math import abs, isnan, isinf, maximum, natural_log, sqrt

Numeric = Union[int, float, Decimal]
NumericType = Type[Union[Numeric, Number]]


# Preliminary graph library exception types,
# and associated standardized input validation functions.

class DirectedGraphNotApplicable(ValueError):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = f"algorithm `{name}` is not applicable to directed graphs"

class DirectedGraphNotSupported(ValueError):
    def __init__(self, name: str, message_addendum: str = ""):
        message = f"algorithm `{name}` does not currently support directed graphs{'' if not message_addendum else f'. {message_addendum}'}"
        super().__init__(message)


class ParameterTypeMismatch(ValueError):
    def __init__(self, name: str, type_, value):
        super().__init__(name)
        self.name = (
            f"parameter `{name}` must be of type {type_.__name__.lower()}, "
            f"but its value {value!r} is of type {type(value)}"
        )

def _assert_type(name: str, value: Numeric, type_: NumericType):
    if not isinstance(value, type_):
        raise ParameterTypeMismatch(name, type_, value)


class ParameterBoundBelowInclusive(ValueError):
    def __init__(self, name: str, value, minimum):
        super().__init__(name)
        self.name = f"parameter `{name}` must be greater than or equal to {minimum}, but is {value!r}"

class ParameterBoundAboveInclusive(ValueError):
    def __init__(self, name: str, value, maximum):
        super().__init__(name)
        self.name = f"parameter `{name}` must be less than or equal to {maximum}, but is {value!r}"

class ParameterBoundBelowExclusive(ValueError):
    def __init__(self, name: str, value, minimum):
        super().__init__(name)
        self.name = f"parameter `{name}` must be strictly greater than {minimum}, but is {value!r}"

class ParameterBoundAboveExclusive(ValueError):
    def __init__(self, name: str, value, maximum):
        super().__init__(name)
        self.name = f"parameter `{name}` must be strictly less than {maximum}, but is {value!r}"

def _assert_inclusive_lower_bound(name: str, value: Numeric, minimum: Numeric):
    if value < minimum:
        raise ParameterBoundBelowInclusive(name, value, minimum)

def _assert_inclusive_upper_bound(name: str, value: Numeric, maximum: Numeric):
    if value > maximum:
        raise ParameterBoundAboveInclusive(name, value, maximum)

def _assert_exclusive_lower_bound(name: str, value: Numeric, minimum: Numeric):
    if value <= minimum:
        raise ParameterBoundBelowExclusive(name, value, minimum)

def _assert_exclusive_upper_bound(name: str, value: Numeric, maximum: Numeric):
    if value >= maximum:
        raise ParameterBoundAboveExclusive(name, value, maximum)


@include_in_docs
class Graph():
    """
    A graph object.

    Parameters
    ----------
    model : Model
        The model to use for the graph.
    directed : bool
        Whether the graph is directed.
    weighted : bool
        Whether the graph is weighted.
    aggregator : str | None
        The aggregation function to use for multi-edges.
    node_concept : Concept | None
        The concept to use for the nodes in the graph.
    edge_concept : Concept | None
        The concept to use for the edges in the graph.
    edge_src_relationship : Relationship | None
        The relationship to use for the source nodes in the graph.
    edge_dst_relationship : Relationship | None
        The relationship to use for the destination nodes in the graph.
    edge_weight_relationship : Relationship | None
        The relationship to use for the edge weights in the graph.

    Attributes
    ----------
    directed : bool
        Whether the graph is directed.
    weighted : bool
        Whether the graph is weighted.
    Node : Concept
        The nodes of the graph.
    Edge : Concept
        The edges of the graph.
    EdgeSrc : Relationship
        The relationship that determines source nodes for edges in the graph.
    EdgeDst : Relationship
        The relationship that determines destination nodes for edges in the graph.
    EdgeWeight : Relationship
        The relationship that determines edge weights in the graph.
    """
    def __init__(self,
            model,
            *,
            directed: bool,
            weighted: bool,
            aggregator: Optional[str] = None,
            node_concept: Optional[Concept] = None,
            edge_concept: Optional[Concept] = None,
            edge_src_relationship: Optional[Relationship] = None,
            edge_dst_relationship: Optional[Relationship] = None,
            edge_weight_relationship: Optional[Relationship] = None,
        ):
        # Validate the required `directed`, `weighted`, and `model` arguments (type).
        assert isinstance(directed, bool), (
            "The `directed` argument must be `True` or `False`, "
            f"but is a `{type(directed).__name__}`."
        )
        assert isinstance(weighted, bool), (
            "The `weighted` argument must be `True` or `False`, "
            f"but is a `{type(weighted).__name__}`."
        )
        assert isinstance(model, Model), (
            "The `model` argument must be a `builder.Model`, "
            f"but is a `{type(model).__name__}`."
        )
        self.directed = directed
        self.weighted = weighted
        self._model = model

        # Validate the optional `aggregator` argument.
        assert aggregator in (None, "sum"), (
            "The `aggregator` argument must be either `None` or 'sum', "
            f"but is {aggregator!r}."
        )
        # Store aggregator mode.
        self._aggregator = aggregator


        # Validate that the optional `node_concept`, `edge_concept`, and related
        # relationship arguments appear in valid combinations:

        if self.weighted:
            edge_args = (edge_concept, edge_src_relationship, edge_dst_relationship, edge_weight_relationship)
        else: # not self.weighted
            edge_args = (edge_concept, edge_src_relationship, edge_dst_relationship)
        any_edge_args = any(arg is not None for arg in edge_args)
        all_edge_args = all(arg is not None for arg in edge_args)

        # If the user provides any of the edge arguments,
        # they must provide a `node_concept`.
        assert not any_edge_args or isinstance(node_concept, Concept), \
            "The `node_concept` argument must be provided when providing `edge_...` arguments."

        # If the graph is weighted, and the user provides any of
        # the edge_ arguments, they must provide all four such arguments.
        if self.weighted:
            assert not any_edge_args or all_edge_args, (
                "For weighted graphs, if any of the `edge_concept`, `edge_src_relationship`, "
                "`edge_dst_relationship`, or `edge_weight_relationship` arguments "
                "is provided, all four such arguments must be provided."
            )
        # If the graph is unweighted, the user may not provide
        # the `edge_weight_relationship` argument, and if they provide
        # any of the edge_ arguments, they must provide all three such arguments.
        else: # not self.weighted
            assert edge_weight_relationship is None, (
                "For unweighted graphs, the `edge_weight_relationship` "
                "argument must not be provided."
            )
            assert not any_edge_args or all_edge_args, (
                "For unweighted graphs, if any of the `edge_concept`, "
                "`edge_src_relationship`, or `edge_dst_relationship` arguments "
                "are provided, all three such arguments must be provided."
            )


        # Now that we know we have a valid combination of the `node_concept`,
        # `edge_concept`, and related relationship arguments,
        # validate their types, models, and schemas:

        # Validate the optional `node_concept` argument's type and model.
        assert isinstance(node_concept, (type(None), Concept)), (
            "The `node_concept` argument must be either a `Concept` or `None`, "
            f"but is a `{type(node_concept).__name__}`."
        )
        assert isinstance(node_concept, type(None)) or (node_concept._model is model), \
            "The given `node_concept` argument must be attached to the given `model` argument."
        self._user_node_concept = node_concept

        # Validate the optional `edge_concept` argument's type and model.
        assert isinstance(edge_concept, (type(None), Concept)), (
            "The `edge_concept` argument must be either a `Concept` or `None`, "
            f"but is a `{type(edge_concept).__name__}`."
        )
        assert edge_concept is None or (edge_concept._model is model), \
            "The given `edge_concept` argument must be attached to the given `model` argument."

        # Validate the `edge_src_relationship` argument's type, model, and schema.
        assert isinstance(edge_src_relationship, (type(None), Relationship)), (
            "The `edge_src_relationship` argument must be either a `Relationship` or `None`, "
            f"but is a `{type(edge_src_relationship).__name__}`."
        )
        assert edge_src_relationship is None or (edge_src_relationship._model is model), \
            "The given `edge_src_relationship` argument must be attached to the given `model` argument."
        if isinstance(edge_src_relationship, Relationship):
            # The combination of assertions above guarantee that `edge_concept`
            # and `node_concept` are not `None` at this point, but the linter
            # can't figure that out. To make the linter happy, re-assert:
            assert edge_concept is not None and node_concept is not None

            assert len(edge_src_relationship._fields) == 2, (
                "The `edge_src_relationship` argument must be a binary relationship, "
                f"but it has {len(edge_src_relationship._fields)} fields."
            )
            assert edge_src_relationship._fields[0].type_str == edge_concept._name, (
                "The first field of the `edge_src_relationship` relationship "
                f"must match the edge concept ('{edge_concept._name}'), "
                f"but is '{edge_src_relationship._fields[0].type_str}'."
            )
            assert edge_src_relationship._fields[1].type_str == node_concept._name, (
                "The second field of the `edge_src_relationship` relationship "
                f"must match the node concept ('{node_concept._name}'), "
                f"but is '{edge_src_relationship._fields[1].type_str}'."
            )

        # Validate the `edge_dst_relationship` argument's type, model, and schema.
        assert isinstance(edge_dst_relationship, (type(None), Relationship)), (
            "The `edge_dst_relationship` argument must be either a `Relationship` or `None`, "
            f"but is a `{type(edge_dst_relationship).__name__}`."
        )
        assert edge_dst_relationship is None or (edge_dst_relationship._model is model), \
            "The given `edge_dst_relationship` argument must be attached to the given `model` argument."
        if isinstance(edge_dst_relationship, Relationship):
            # The combination of assertions above guarantee that `edge_concept`
            # and `node_concept` are not `None` at this point, but the linter
            # can't figure that out. To make the linter happy, re-assert:
            assert edge_concept is not None and node_concept is not None

            assert len(edge_dst_relationship._fields) == 2, (
                "The `edge_dst_relationship` argument must be a binary relationship, "
                f"but it has {len(edge_dst_relationship._fields)} fields."
            )
            assert edge_dst_relationship._fields[0].type_str == edge_concept._name, (
                "The first field of the `edge_dst_relationship` relationship "
                f"must match the edge concept ('{edge_concept._name}'), "
                f"but is '{edge_dst_relationship._fields[0].type_str}'."
            )
            assert edge_dst_relationship._fields[1].type_str == node_concept._name, (
                "The second field of the `edge_dst_relationship` relationship "
                f"must match the node concept ('{node_concept._name}'), "
                f"but is '{edge_dst_relationship._fields[1].type_str}'."
            )

        # Validate the `edge_weight_relationship` argument's type, model, and schema.
        assert isinstance(edge_weight_relationship, (type(None), Relationship)), (
            "The `edge_weight_relationship` argument must be either a `Relationship` or `None`, "
            f"but is a `{type(edge_weight_relationship).__name__}`."
        )
        assert edge_weight_relationship is None or (edge_weight_relationship._model is model), \
            "The given `edge_weight_relationship` argument must be attached to the given `model` argument."
        if isinstance(edge_weight_relationship, Relationship):
            # The combination of assertions above guarantee that `edge_concept`
            # and `node_concept` are not `None` at this point, but the linter
            # can't figure that out. To make the linter happy, re-assert:
            assert edge_concept is not None and node_concept is not None

            assert len(edge_weight_relationship._fields) == 2, (
                "The `edge_weight_relationship` argument must be a binary relationship, "
                f"but it has {len(edge_weight_relationship._fields)} fields."
            )
            assert edge_weight_relationship._fields[0].type_str == edge_concept._name, (
                "The first field of the `edge_weight_relationship` relationship "
                f"must match the edge concept ('{edge_concept._name}'), "
                f"but is '{edge_weight_relationship._fields[0].type_str}'."
            )
            assert edge_weight_relationship._fields[1].type_str == "Float", (
                "The second field of the `edge_weight_relationship` relationship "
                f"must have type 'Float', but is '{edge_weight_relationship._fields[1].type_str}'."
            )

        # Finally store any user-provided node concept,
        # edge concept, and associated relationship arguments.
        self._user_node_concept = node_concept
        self._user_edge_concept = edge_concept
        self._user_edge_src_relationship = edge_src_relationship
        self._user_edge_dst_relationship = edge_dst_relationship
        self._user_edge_weight_relationship = edge_weight_relationship


        # Unless the user passes in existing `Concept`s to serve as
        # the graph's `Node` and/or `Edge` `Concept`s, this class generates
        # new `Node` and/or `Edge` concepts with quasi-unique name-strings,
        # attempting to avoid name-string collisions while retaining
        # as much determinism, consistency, and readability as possible:
        #
        # The following counter tracks the number of graphs attached to the model,
        # initialized to zero but immediately incremented to start from one.
        # (`setattr` and `getattr` are used to make linting happy.)
        if not hasattr(model, "_graph_counter"):
            setattr(model, "_graph_counter", 0)
        setattr(model, "_graph_counter", getattr(model, "_graph_counter", 0) + 1)
        #
        # The generated `Node` and `Edge` `Concept` name-strings incorporate
        # this counter to allow coexistence of multiple graphs in the same model.
        # (`getattr` is used to make linting happy.)
        self._graph_id = getattr(model, "_graph_counter")
        self._NodeConceptStr = node_concept._name if node_concept else f"graph{self._graph_id}_Node"
        self._EdgeConceptStr = edge_concept._name if edge_concept else f"graph{self._graph_id}_Edge"

        # Initialize cache for visualization data.
        self._last_visualization_fetch = None

        # The remainder of the library is lazily defined and attached
        # to the model through cached-property member fields of this class.


    @cached_property
    def Node(self) -> Concept:
        """Lazily define and cache the self.Node concept."""
        return self._user_node_concept or self._model.Concept(self._NodeConceptStr)


    @cached_property
    def Edge(self):
        """Lazily define and cache the self.Edge concept and friends,
        by passing through to self._EdgeComplex."""
        _Edge, _, _, _ = self._EdgeComplex
        return _Edge

    @cached_property
    def EdgeSrc(self):
        """Lazily define and cache the self.EdgeSrc relationship and friends,
        by passing through to self._EdgeComplex."""
        _, _EdgeSrc, _, _ = self._EdgeComplex
        return _EdgeSrc

    @cached_property
    def EdgeDst(self):
        """Lazily define and cache the self.EdgeDst relationship and friends,
        by passing through to self._EdgeComplex."""
        _, _, _EdgeDst, _ = self._EdgeComplex
        return _EdgeDst

    @cached_property
    def EdgeWeight(self):
        """Lazily define and cache the self.EdgeWeight relationship and friends,
        by passing through to self._EdgeComplex."""
        _, _, _, _EdgeWeight = self._EdgeComplex
        return _EdgeWeight

    @cached_property
    def _EdgeComplex(self):
        """
        Lazily define and cache self._EdgeComplex, which consists of
        what becomes the self.Edge concept, the self.EdgeSrc relationship,
        the self.EdgeDst relationship, the self.EdgeWeight relationship,
        and all associated logic. Each of the preceding properties
        passes through to this property, such that all of the above
        are lazily defined and cached together, once.
        """
        if self._user_edge_concept:
            # The validations in __init__ guarantee that if the user provided
            # an edge concept, they must have provided all associated edge
            # relationships appropriate for their (un/weighted) graph type.
            assert self._user_edge_src_relationship is not None  # appease linter
            assert self._user_edge_dst_relationship is not None  # appease linter
            # In this case, use the provided concept and relationships
            # rather than generating new ones.
            _Edge = self._user_edge_concept
            _EdgeSrc = self._user_edge_src_relationship
            _EdgeDst = self._user_edge_dst_relationship
            if self.weighted:
                assert self._user_edge_weight_relationship is not None  # appease linter
                _EdgeWeight = self._user_edge_weight_relationship
            else: # not self.weighted
                # For unweighted graphs, generate a weight relationship
                # to simplify the logic below.
                _EdgeWeight = self._model.Relationship(f"{{edge:{self._EdgeConceptStr}}} has weight {{weight:Float}}")

            # Define diagnostic messages specialized for this case.
            _edge_must_have_source_message = (
                f"Every edge (`Graph.Edge`, bound to the `{_Edge._name}` concept "
                f"via the `edge_concept` argument), must have a source (`Graph.EdgeSrc`, "
                f"bound to the `edge_src_relationship` argument)."
            )
            _edge_must_have_destination_message = (
                f"Every edge (`Graph.Edge`, bound to the `{_Edge._name}` concept "
                f"via the `edge_concept` argument), must have a destination (`Graph.EdgeDst`, "
                f"bound to the `edge_dst_relationship` argument)."
            )
            _edge_must_have_weight_message = (
                f"For weighted graphs, every edge (`Graph.Edge`, bound to the `{_Edge._name}` concept "
                f"via the `edge_concept` argument), must have a weight (`Graph.EdgeWeight`, "
                f"bound to the `edge_weight_relationship` argument)."
            )

        else: # not self._user_edge_concept
            # The user did not provide an edge concept and associated relationships,
            # so generate that concept and those relationships.
            _Edge = self._model.Concept(self._EdgeConceptStr)
            # In this case we can safely make the associated relationships
            # properties of the edge concept, improving user experience.
            _Edge.src = self._model.Relationship(f"{{edge:{self._EdgeConceptStr}}} has source {{src:{self._NodeConceptStr}}}")
            _Edge.dst = self._model.Relationship(f"{{edge:{self._EdgeConceptStr}}} has destination {{dst:{self._NodeConceptStr}}}")
            _Edge.weight = self._model.Relationship(f"{{edge:{self._EdgeConceptStr}}} has weight {{weight:Float}}")
            # Nonetheless we must bind them as follows to share the downstream logic.
            _EdgeSrc = _Edge.src
            _EdgeDst = _Edge.dst
            _EdgeWeight = _Edge.weight

            # Define diagnostic messages specialized for this case.
            _edge_must_have_source_message = \
                "Every edge (`Graph.Edge`) must have a source (`Graph.Edge.src`)."
            _edge_must_have_destination_message = \
                "Every edge (`Graph.Edge`) must have a destination (`Graph.Edge.dst`)."
            _edge_must_have_weight_message = \
                "Every edge (`Graph.Edge`) must have a weight (`Graph.Edge.weight`)."

        # All `Edge`s must have a `src`:
        where(_Edge, not_(_EdgeSrc(_Edge, self.Node))).define(
            Error.new(message=_edge_must_have_source_message, edge=_Edge)
        )

        # All `Edge`s must have a `dst`:
        where(_Edge, not_(_EdgeDst(_Edge, self.Node))).define(
            Error.new(message=_edge_must_have_destination_message, edge=_Edge)
        )

        # If weighted, ...
        if self.weighted:
            src, dst = self.Node.ref(), self.Node.ref()
            # ... all `Edge`s must have a `weight`:
            where(
                _Edge, not_(_EdgeWeight(_Edge, Float)), # Necessary for check.
                _EdgeSrc(_Edge, src), _EdgeDst(_Edge, dst), # Solely for message.
            ).define(
                Error.new(
                    message=_edge_must_have_weight_message,
                    edge=_Edge, source=src, destination=dst,
                )
            )
            # ... edge weights must not be NaN:
            where(
                _Edge, _EdgeWeight(_Edge, Float), isnan(Float), # Necessary for check.
                _EdgeSrc(_Edge, src), _EdgeDst(_Edge, dst), # Solely for message.
            ).define(
                Error.new(
                    message="Edge weights must not be NaN.",
                    edge=_Edge, source=src, destination=dst, weight=Float,
                )
            )
            # ... edge weights must not be infinite:
            where(
                _Edge, _EdgeWeight(_Edge, Float), isinf(Float), # Necessary for check.
                _EdgeSrc(_Edge, src), _EdgeDst(_Edge, dst), # Solely for message.
            ).define(
                Error.new(
                    message="Edge weights must not be infinite.",
                    edge=_Edge, source=src, destination=dst, weight=Float,
                )
            )
            # ... and edge weights must not be negative:
            where(
                _Edge, _EdgeWeight(_Edge, Float), Float < 0.0, # Necessary for check.
                _EdgeSrc(_Edge, src), _EdgeDst(_Edge, dst), # Solely for message.
                not_(isnan(Float)), # To work around https://relationalai.atlassian.net/browse/RAI-40437
            ).define(
                Error.new(
                    message="Edge weights must not be negative.",
                    edge=_Edge, source=src, destination=dst, weight=Float,
                )
            )
        # If not weighted, no `Edge`s may have a `weight`:
        else: # not self.weighted:
            # Note that the message for this error is a bit lighter than
            # for the error where the user must, but did not, provide a weight,
            # as other argument validation more or less prevents this case from
            # occurring when the user provides their own concepts/relationships.
            src, dst = self.Node.ref(), self.Node.ref()
            where(
                _Edge, _EdgeWeight(_Edge, Float), # Necessary for check.
                _EdgeSrc(_Edge, src), _EdgeDst(_Edge, dst), # Solely for message.
            ).define(
                Error.new(
                    message=(
                        "In an unweighted graph, no edge (`Graph.Edge`) "
                        "may have a weight (`Graph.Edge.weight`)."
                    ),
                    edge=_Edge, source=src, destination=dst, weight=Float,
                )
            )

        # If the aggregator is None and the graph is directed,
        # no multi-edges are allowed; i.e., distinct edges
        # may not have the same source and destination.
        if self._aggregator is None and self.directed:
            edge_a, edge_b = _Edge.ref(), _Edge.ref()
            edge_a_src, edge_a_dst = self.Node.ref(), self.Node.ref()
            edge_b_src, edge_b_dst = self.Node.ref(), self.Node.ref()
            where(
                edge_a, edge_b,
                edge_a < edge_b, # implies edge_a != edge_b
                _EdgeSrc(edge_a, edge_a_src), _EdgeDst(edge_a, edge_a_dst),
                _EdgeSrc(edge_b, edge_b_src), _EdgeDst(edge_b, edge_b_dst),
                edge_a_src == edge_b_src, edge_a_dst == edge_b_dst,
            ).define(
                Error.new(
                    message=(
                        "Multi-edges are not allowed when `aggregator=None`. "
                        "(I.e., distinct edges may not have the same source and destination.)"
                    ),
                    edge_a=edge_a,
                    edge_b=edge_b,
                    common_source=edge_a_src,
                    common_destination=edge_a_dst,
                )
            )
        # If the aggregator is None and the graph is undirected,
        # no multi-edges (express or implied) are allowed; i.e.
        # 1) distinct edges may not have the same source and destination; and
        # 2) distinct edges may not have one node's source matching
        # the other node's destination and vice versa.
        elif self._aggregator is None and not self.directed:
            edge_a, edge_b = _Edge.ref(), _Edge.ref()
            edge_a_src, edge_a_dst = self.Node.ref(), self.Node.ref()
            edge_b_src, edge_b_dst = self.Node.ref(), self.Node.ref()
            where(
                edge_a, edge_b,
                edge_a < edge_b, # implies edge_a != edge_b
                _EdgeSrc(edge_a, edge_a_src), _EdgeDst(edge_a, edge_a_dst),
                _EdgeSrc(edge_b, edge_b_src), _EdgeDst(edge_b, edge_b_dst),
                where(edge_a_src == edge_b_src, edge_a_dst == edge_b_dst) |
                where(edge_a_src == edge_b_dst, edge_a_dst == edge_b_src)
            ).define(
                Error.new(
                    message=(
                        "Multi-edges are not allowed when `aggregator=None`. "
                        "(I.e., distinct edges may not have the same source and destination, "
                        "nor one node's source matching the other node's destination "
                        "and vice versa."
                    ),
                    edge_a=edge_a,
                    edge_b=edge_b,
                    edge_a_src=edge_a_src,
                    edge_b_src=edge_b_src,
                    edge_a_dst=edge_a_dst,
                    edge_b_dst=edge_b_dst,
                )
            )

        return _Edge, _EdgeSrc, _EdgeDst, _EdgeWeight


    @cached_property
    def _edge(self):
        """
        Lazily define and cache the `self._edge` relationship,
        consuming the `Edge` concept's `EdgeSrc` and `EdgeDst` relationships.
        """
        _edge_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has edge to {{dst:{self._NodeConceptStr}}}")

        Edge, EdgeSrc, EdgeDst = self.Edge, self.EdgeSrc, self.EdgeDst
        src, dst = self.Node.ref(), self.Node.ref()
        if self.directed:
            where(
                Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst)
            ).define(
                _edge_rel(src, dst)
            )
        elif not self.directed:
            where(
                Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst)
            ).define(
                _edge_rel(src, dst),
                _edge_rel(dst, src)
            )

        return _edge_rel

    @cached_property
    def _weight(self):
        """
        Lazily define and cache the `self._weight` relationship,
        consuming the `Edge` concept's `EdgeSrc`, `EdgeDst`, and `EdgeWeight` relationships.
        """
        _weight_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has edge to {{dst:{self._NodeConceptStr}}} with weight {{weight:Float}}")

        Edge, EdgeSrc, EdgeDst, EdgeWeight = self.Edge, self.EdgeSrc, self.EdgeDst, self.EdgeWeight
        src, dst, weight = self.Node.ref(), self.Node.ref(), Float.ref()
        if self.directed and self.weighted:
            if self._aggregator == "sum":
                # Sum-aggregate multi-edge weights per (src, dst).
                summed_weight = Float.ref()
                where(
                    summed_weight := \
                        sum(
                            Edge, weight
                        ).per(
                            src, dst
                        ).where(
                            Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst), EdgeWeight(Edge, weight)
                        )
                ).define(
                    _weight_rel(src, dst, summed_weight)
                )
            else: # No aggregation; simply enumerate weights.
                where(
                    Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst), EdgeWeight(Edge, weight)
                ).define(
                    _weight_rel(src, dst, weight)
                )
        elif self.directed and not self.weighted:
            where(
                Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst)
            ).define(
                _weight_rel(src, dst, 1.0)
            )
        elif not self.directed and self.weighted:
            if self._aggregator == "sum":
                # Canonicalize unordered pairs.
                a, b, w = self.Node.ref(), self.Node.ref(), Float.ref()
                canon_edge, canon_src, canon_dst, canon_weight = \
                    self.Edge.ref(), self.Node.ref(), self.Node.ref(), Float.ref()
                canon_edge, canon_src, canon_dst, canon_weight = union(
                    where(Edge, EdgeSrc(Edge, a), EdgeDst(Edge, b), EdgeWeight(Edge, w), a <= b).select(Edge, a, b, w),
                    where(Edge, EdgeSrc(Edge, a), EdgeDst(Edge, b), EdgeWeight(Edge, w), b < a).select(Edge, b, a, w),
                )
                # The above could be replaced with the following simpler/cleaner
                # version once support for minimum/maximum/friends over concepts lands:
                # canon_edge, canon_src, canon_dst, canon_weight = select(
                #     Edge, minimum(a, b), maximum(a, b), w
                # ).where(
                #     EdgeSrc(Edge, a), EdgeDst(Edge, b), EdgeWeight(Edge, w)
                # )

                # Sum weights per pair, then emit both orientations.
                summed_weight = Float.ref()
                where(
                    summed_weight := \
                        sum(
                            canon_edge, canon_weight
                        ).per(
                            canon_src, canon_dst
                        ).where(
                            canon_edge, canon_src, canon_dst, canon_weight
                        )
                ).define(
                    _weight_rel(canon_src, canon_dst, summed_weight),
                    _weight_rel(canon_dst, canon_src, summed_weight),
                )
            else: # No aggregation; enumerate and emit both orientations.
                where(
                    Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst), EdgeWeight(Edge, weight)
                ).define(
                    _weight_rel(src, dst, weight),
                    _weight_rel(dst, src, weight)
                )
        elif not self.directed and not self.weighted:
            where(
                Edge, EdgeSrc(Edge, src), EdgeDst(Edge, dst)
            ).define(
                _weight_rel(src, dst, 1.0),
                _weight_rel(dst, src, 1.0)
            )

        return _weight_rel


    # Begin Visualization ------------------------------------------------------

    def _fetch_for_visualization(self):
        """
        This method fetches (that is, collects client-side) all nodes, edges,
        and their public binary properties, for visualization. It caches that
        information in self._last_visualization_fetch for downstream use.
        """
        # `output`, cached in `self._last_visualization_fetch`, is
        # a nested dictionary. At the top level it contains
        # keys `nodes` and `edges` that map to dictionaries.
        #
        # The `nodes` dictionary contains a key for each node hash,
        # which maps to a dictionary. That dictionary contains a key for
        # each public binary property the node has a value for,
        # mapped to that value.
        #
        # The `edges` dictionary contains a key for each edge hash,
        # which maps to a dictionary. That dictionary contains a 'src'
        # key, which maps to the source node of the edge, and a 'dst'
        # key, which maps to the destination node of the edge. It also contains
        # a key for each public binary property the edge has a value for,
        # mapped to its value for that edge. This structure captures multiedges.
        #
        # TODO: When bandwidth allows, also need special handling for 'weight',
        #   in the case that the user provided a weight relationship that
        #   isn't a property of the edge concept.
        output = {
            "nodes": dict(),
            "edges": dict()
        }

        # Fetch all node hashes, and store in `output`.
        for (node_hash,) in select(self.Node):
            output["nodes"][node_hash] = {}

        # Fetch all public binary properties for those nodes, and store in `output`.
        node_properties = self.Node._relationships
        for prop_name, prop_relationship in node_properties.items():
            # Properties with names beginning with an underscore are private,
            # and should not be visualized; skip fetching them.
            if prop_name.startswith('_'):
                continue

            # Handle only binary properties; skip fetching all others.
            if len(prop_relationship._field_refs) != 2:
                continue

            # The property should have structure
            # `prop_relationship(node_var, prop_var)`;
            # construct a select query to retrieve all such two-tuples.
            node_var = self.Node.ref()
            prop_var = prop_relationship._field_refs[1].ref()
            prop_query = select(node_var, prop_var).where(prop_relationship(node_var, prop_var))

            # Wrap evaluation of the query into a try-except,
            # as the property may not be populated for all nodes,
            # or the query might otherwise fail; IOW this is best effort.
            try:
                for (node_hash, prop_value) in prop_query:
                    output["nodes"][node_hash][prop_name] = prop_value
            except Exception:
                continue # Best effort.

        # Fetch all edge hashes, sources, and destinations, and store in `output`.
        src, dst = self.Node.ref(), self.Node.ref()
        edges_query = \
            select(
                self.Edge, src, dst,
            ).where(
                self.EdgeSrc(self.Edge, src),
                self.EdgeDst(self.Edge, dst),
            )
        for (edge_hash, src_hash, dst_hash) in edges_query:
            output["edges"][edge_hash] = {
                "src": src_hash,
                "dst": dst_hash
            }

        # Fetch all public binary properties for those edges, and store in `output`.
        edge_properties = self.Edge._relationships
        for prop_name, prop_relationship in edge_properties.items():
            # Properties with names beginning with an underscore are private,
            # and should not be visualized; skip fetching them.
            if prop_name.startswith('_'):
                continue

            # Handle only binary properties; skip fetching all others.
            if len(prop_relationship._field_refs) != 2:
                continue

            # The source and destination for each edge were extracted above.
            # If the source and destination relationships also happen to be
            # properties of the edge concept, they should not be visualized;
            # skip fetching them.
            if prop_relationship is self.EdgeSrc or prop_relationship is self.EdgeDst:
                continue

            # The property should have structure
            # `prop_relationship(edge_var, prop_var)`;
            # construct a select query to retrieve all such two-tuples.
            edge_var = self.Edge.ref()
            prop_var = prop_relationship._field_refs[1].ref()
            prop_query = select(edge_var, prop_var).where(prop_relationship(edge_var, prop_var))

            # Wrap evaluation of the query into a try-except,
            # as the property may not be populated for all nodes,
            # or the query might otherwise fail; IOW this is best effort.
            try:
                for (edge_hash, prop_value) in prop_query:
                    output["edges"][edge_hash][prop_name] = prop_value
            except Exception:
                continue # Best effort.

        self._last_visualization_fetch = output
        return output


    # Helper for the _build_gJGF_dictionary method below.
    def _props_to_gJGF_metadata(self, style_props, node_or_edge_props_copy):
        """
        This method takes a copy of a set of node or edge properties, and
        a set of gravis style directives, and combines them into gJGF metadata
        for nodes and edges.
        """
        # Given this method receives a copy, it can be mutated and returned.
        metadata = node_or_edge_props_copy

        # Apparently values for style properties can be callables,
        # in which case the right thing to do is to add the style
        # property's key to the metadata, populating its value
        # with the application of the callable to the full metadata.
        for style_prop_key, style_prop_value in style_props.items():
            if callable(style_prop_value):
                metadata[style_prop_key] = style_prop_value(metadata)

        # Some property value types aren't supported by JSON;
        # convert them appropriately here.
        for prop_key, prop_value in metadata.items():
            # Decimals are not supported, convert to floats.
            if isinstance(prop_value, Decimal):
                metadata[prop_key] = float(prop_value)
            # NumPy integers are not supported, convert to ints.
            if isinstance(prop_value, numpy.integer):
                metadata[prop_key] = int(prop_value)

        # For some reason, the existence of "id" in the metadata
        # results in edges not getting displayed in the visualization,
        # so we remove it.
        if "id" in metadata:
            del metadata["id"]

        return metadata


    def _build_gJGF_dictionary(
            self,
            graph_data: dict,
            user_style: Optional[dict] = None,
        ) -> dict:
        """
        From graph data in the format produced by `_fetch_visualization_data`,
        and any user-provided gravis style directives, build a gJGF (i.e.,
        "graph in JSON Graph Format") representation of the graph and styling,
        as a dictionary. (gJGF is the format used by the gravis library.)
        """

        # Define default visual properties for nodes and edges.
        default_visual_properties = {
            "node": {
                "color": "black",
                "opacity": 1,
                "size": 10,
                "shape": "circle",
                "border_color": "black",
                "border_size": 1,
                "label_color": "black",
                "label_size": 10,
            },
            "edge": {
                "color": "#999",
                "opacity": 1,
                "size": 2,
                "shape": "circle",
                "border_color": "#999",
                "border_size": 1,
                "label_color": "black",
                "label_size": 10,
                "arrow_size": 4,
                "arrow_color": "#999",
            }
        }

        # If the user provided gravis styling directives, merge them into
        # the default style, with user directives winning collisions.
        merged_style = default_visual_properties
        if user_style:
            for category in ["node", "edge"]:
                for style_prop_key, style_prop_value in user_style.get(category, {}).items():
                    if not callable(style_prop_value):
                        merged_style[category][style_prop_key] = style_prop_value

        # merged_style is a nested dictionary structure. At the top level,
        # it maps "node" and "edge" keys to values that are dictionaries.
        # Those dictionary values map style property keys to style property values.
        #
        # Here we build a flattened form of that dictionary. Specifically,
        # the top-level "node" and "edge" keys are flattened away, pushed
        # into prefixes on the style property keys in the corresponding
        # original value dictionaries. E.g., merged_style["node"]["style_prop"]
        # becomes flat_style["node_style_prop"].
        #
        # There is one wrinkle: the "arrow" properties are special and need to be
        # handled differently. Specifically, we do not want to add the "node"
        # or "edge" prefixes to them.
        _prefix_exclusion_map = {
            "arrow_size": "arrow_size",
            "arrow_color": "arrow_color",
        }
        flat_style = {}
        for prefix, style_props in merged_style.items():
            for style_prop_key, style_prop_value in style_props.items():
                if style_prop_key in _prefix_exclusion_map:
                    new_style_prop_key = _prefix_exclusion_map[style_prop_key]
                else:
                    new_style_prop_key = f"{prefix}_{style_prop_key}"
                flat_style[new_style_prop_key] = style_prop_value

        # Finally build and return the gJGF dictionary.
        return {
            "graph": {
                "directed": self.directed,
                "metadata": flat_style,
                "nodes": {
                    node_hash: {
                        **({"label": str(node_props["label"])} if "label" in node_props else {}),
                        "metadata": self._props_to_gJGF_metadata(
                            merged_style["node"],
                            node_props.copy()
                        ),
                    }
                    for (node_hash, node_props) in graph_data["nodes"].items()
                },
                "edges": [
                    {
                        "source": edge_props["src"],
                        "target": edge_props["dst"],
                        "metadata": self._props_to_gJGF_metadata(
                            merged_style["edge"],
                            # Exclude the source and destination from
                            # the properties sent through as metadata.
                            {k: v for k, v in edge_props.items() if k not in ("src", "dst")}
                        )
                    }
                    for (edge_hash, edge_props) in graph_data["edges"].items()
                ],
            }
        }


    def visualize(
            self,
            gravis_style=None,
            use_fetch_cache=False,
            use_gravis_three=False,
            **user_kwargs_for_gravis,
        ):
        """
        Visualize the graph with `gravis`.

        Set the `gravis_style` keyword argument, a dictionary containing
        gravis styling directives for nodes and edges, to customize
        the appearance of the graph.

        By default, this method will fetch all necessary (node, edge, and
        node/edge property) data and cache it locally. To use the most
        recently cached data instead of fetching fresh data, set
        the `use_fetch_cache` argument to `True`; this is useful
        to tighten the iteration loop when customizing the visualization.

        By default, this method uses the `gravis.vis(...)` method for visualization.
        `vis` builds an interactive, two-dimensional graph view using `vis.js`
        (DOM/canvas). This method is simple and lightweight, but lacks some
        styling features (e.g., separate arrow colors and per-element opacity),
        so those options are ignored. Alternatively, set the `use_gravis_three`
        argument to `True` to use `gravis.three(...)`, which builds an interactive,
        three-dimensional graph view using `3d-force-graph`, which in turn uses
        `three.js`/WebGL. You get a draggable three-dimensional scene with
        force-layout physics; some features (e.g., node borders, edge labels)
        aren’t available compared to other back-ends.

        Any other keyword arguments will be passed through to `gravis`, merged
        with the following default keyword arguments.
        ```
            "node_label_data_source": "label",
            "edge_label_data_source": "label",
            "show_edge_label": True,
            "edge_curvature": 0.4,
        ```
        Colliding keyword arguments will override these defaults.

        TODO: Clean up / format-normalize this docstring at some point.
        """
        # TODO: The present implementation is woefully poorly exercised,
        #   to be improved when bandwidth allows.

        # Confirm necessary conditions for visualization support in Snowbook environments,
        # and bail if those conditions are not met.
        from relationalai.environments import runtime_env, SnowbookEnvironment
        if isinstance(runtime_env, SnowbookEnvironment) and runtime_env.runner != "container":
            from relationalai.errors import UnsupportedVisualizationError
            raise UnsupportedVisualizationError()

        # By default, freshly fetch all necessary node, edge, and
        # node/edge property data (and cache it locally). If the user
        # specified `use_fetch_cache`, use the most recently cached data
        # instead of fetching fresh data.
        graph_data = self._last_visualization_fetch if use_fetch_cache else None
        if not graph_data:
            graph_data = self._fetch_for_visualization()

        # From the fetched graph data any user-provided style directives
        # (via `gravis_style`), build a gJGF ("graph in JSON Graph Format",
        # the format that gravis understands) dictionary describing
        # the graph and how to style/visualize it.
        gJGF_dictionary = self._build_gJGF_dictionary(
            graph_data=graph_data,
            user_style=gravis_style,
        )

        # If the user provided additional keyword arguments to pass through
        # to gravis, merge those with the following default keyword arguments.
        # (The user's keyword arguments win collisions.)
        kwargs_for_gravis = {
            "node_label_data_source": "label",
            "edge_label_data_source": "label",
            "show_edge_label": True,
            "edge_curvature": 0.4,
        } | user_kwargs_for_gravis

        # By default, visualize with `gravis.vis`. If the user specified
        # `use_gravis_three`, visualize with `gravis.three` instead.
        gravis_method = gravis.vis if not use_gravis_three else gravis.three

        # Finally call gravis.
        gravis_rendering = gravis_method(
            gJGF_dictionary,
            **kwargs_for_gravis
        )

        return gravis_rendering

    # End Visualization --------------------------------------------------------


    # The following three `_count_[in,out]neighbor` relationships are
    # primarily for internal consumption. They differ from corresponding
    # `_[in,out]degree` relationships in that they yield empty
    # rather than zero absent [in,out]neighbors.

    @cached_property
    def _count_neighbor(self):
        """Lazily define and cache the self._count_neighbor relationship."""
        return self._create_count_neighbor_relationship(nodes_subset=None)

    def _count_neighbor_of(self, nodes_subset: Relationship):
        """
        Create a _count_neighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_count_neighbor_relationship(nodes_subset=nodes_subset)

    def _create_count_neighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _count_neighbor_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has neighbor count {{count:Integer}}")

        # Choose the appropriate neighbor relationship based on whether we have constraints
        if nodes_subset is None:
            # No constraint - use cached neighbor relationship
            neighbor_rel = self._neighbor
        else:
            # Constrained to nodes in the subset - use constrained neighbor relationship
            neighbor_rel = self._neighbor_of(nodes_subset)

        # Apply the same counting logic for both cases
        src, dst = self.Node.ref(), self.Node.ref()
        where(neighbor_rel(src, dst)).define(_count_neighbor_rel(src, count(dst).per(src)))

        return _count_neighbor_rel

    @cached_property
    def _count_inneighbor(self):
        """Lazily define and cache the self._count_inneighbor relationship."""
        return self._create_count_inneighbor_relationship(nodes_subset=None)

    def _count_inneighbor_of(self, nodes_subset: Relationship):
        """
        Create a _count_inneighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_count_inneighbor_relationship(nodes_subset=nodes_subset)

    def _create_count_inneighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _count_inneighbor_rel = self._model.Relationship(f"{{dst:{self._NodeConceptStr}}} has inneighbor count {{count:Integer}}")

        # Choose the appropriate inneighbor relationship based on whether we have constraints
        if nodes_subset is None:
            # No constraint - use cached inneighbor relationship
            inneighbor_rel = self._inneighbor
        else:
            # Constrained to nodes in the subset - use constrained inneighbor relationship
            inneighbor_rel = self._inneighbor_of(nodes_subset)

        # Apply the same counting logic for both cases
        dst, src = self.Node.ref(), self.Node.ref()
        where(inneighbor_rel(dst, src)).define(_count_inneighbor_rel(dst, count(src).per(dst)))

        return _count_inneighbor_rel

    @cached_property
    def _count_outneighbor(self):
        """Lazily define and cache the self._count_outneighbor relationship."""
        return self._create_count_outneighbor_relationship(nodes_subset=None)

    def _count_outneighbor_of(self, nodes_subset: Relationship):
        """
        Create a _count_outneighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_count_outneighbor_relationship(nodes_subset=nodes_subset)

    def _create_count_outneighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _count_outneighbor_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has outneighbor count {{count:Integer}}")

        # Choose the appropriate outneighbor relationship based on whether we have constraints
        if nodes_subset is None:
            # No constraint - use cached outneighbor relationship
            outneighbor_rel = self._outneighbor
        else:
            # Constrained to nodes in the subset - use constrained outneighbor relationship
            outneighbor_rel = self._outneighbor_of(nodes_subset)

        # Apply the same counting logic for both cases
        src, dst = self.Node.ref(), self.Node.ref()
        where(outneighbor_rel(src, dst)).define(_count_outneighbor_rel(src, count(dst).per(src)))

        return _count_outneighbor_rel


    # The following fragments are primarily for internal consumption,
    # presently in use by the `cosine_similarity` and
    # `jaccard_similarity` relationships.

    def _count_common_outneighbor_fragment(self, node_u, node_v):
        """
        Helper for cosine_similarity and jaccard_similarity that returns a fragment
        that counts the common outneighbors of given nodes `node_u` and `node_v`.
        """
        common_outneighbor_node = self.Node.ref()
        return (
            count(common_outneighbor_node)
            .per(node_u, node_v)
            .where(
                self._outneighbor(node_u, common_outneighbor_node),
                self._outneighbor(node_v, common_outneighbor_node),
            )
        )

    def _wu_dot_wv_fragment(self, node_u, node_v):
        """
        Helper for cosine_similarity that returns a fragment that produces an
        un-normalized inner product between the outneighbor vectors of given
        nodes `node_u` and `node_v`.
        """
        node_k, wu, wv = self.Node.ref(), Float.ref(), Float.ref()
        return (
            sum(node_k, wu * wv)
            .per(node_u, node_v)
            .where(
                self._weight(node_u, node_k, wu),
                self._weight(node_v, node_k, wv),
            )
        )


    @include_in_docs
    def num_nodes(self) -> Relationship:
        """Returns a unary relationship containing the number of nodes in the graph.

        Returns
        -------
        Relationship
            A unary relationship containing the number of nodes in the graph.

        Relationship Schema
        -------------------
        ``num_nodes(count)``

        * **count** (*Integer*): The number of nodes in the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up the graph and concepts
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define some nodes
        >>> node1, node2, node3, node4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(node1, node2, node3, node4)
        >>>
        >>> # 3. Define the full set of edges
        >>> define(
        ...     Edge.new(src=node1, dst=node2),
        ...     Edge.new(src=node2, dst=node3),
        ...     Edge.new(src=node3, dst=node3),
        ...     Edge.new(src=node2, dst=node4),
        ... )
        >>>
        >>> # 4. The relationship contains the number of nodes
        >>> graph.num_nodes().inspect()
        ▰▰▰▰ Setup complete
           int
        0    4

        See Also
        --------
        num_edges

        """
        return self._num_nodes

    @cached_property
    def _num_nodes(self):
        """Lazily define and cache the self._num_nodes relationship."""
        _num_nodes_rel = self._model.Relationship("The graph has {num_nodes:Integer} nodes")
        define(_num_nodes_rel(count(self.Node) | 0))
        return _num_nodes_rel


    @include_in_docs
    def num_edges(self):
        """Returns a unary relationship containing the number of edges in the graph.

        Returns
        -------
        Relationship
            A unary relationship containing the number of edges in the graph.

        Relationship Schema
        -------------------
        ``num_edges(count)``

        * **count** (*Integer*): The number of edges in the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up the graph and concepts
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define some nodes
        >>> node1, node2, node3, node4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(node1, node2, node3, node4)
        >>>
        >>> # 3. Define the edges
        >>> define(
        ...     Edge.new(src=node1, dst=node2),
        ...     Edge.new(src=node2, dst=node3),
        ...     Edge.new(src=node3, dst=node3),
        ...     Edge.new(src=node2, dst=node4),
        ... )
        >>>
        >>> # 4. The relationship contains the number of edges
        >>> graph.num_edges().inspect()
        ▰▰▰▰ Setup complete
           int
        0    4

        See Also
        --------
        num_nodes

        """
        return self._num_edges

    @cached_property
    def _num_edges(self):
        """Lazily define and cache the self._num_edges relationship."""
        _num_edges_rel = self._model.Relationship("The graph has {num_edges:Integer} edges")

        src, dst = self.Node.ref(), self.Node.ref()
        if self.directed:
            define(_num_edges_rel(count(src, dst, self._edge(src, dst)) | 0))
        elif not self.directed:
            define(_num_edges_rel(count(src, dst, self._edge(src, dst), src <= dst) | 0))

        return _num_edges_rel


    @include_in_docs
    def neighbor(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship containing all neighbor pairs in the graph.

        For directed graphs, a node's neighbors include both its in-neighbors
        and out-neighbors.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the neighbor computation: only
            neighbors of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and one
            of its neighbors.

        Relationship Schema
        -------------------
        ``neighbor(node, neighbor_node)``

        * **node** (*Node*): A node in the graph.
        * **neighbor_node** (*Node*): A neighbor of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                           |
        | :--------- | :-------- | :---------------------------------------------- |
        | Undirected | Yes       |                                                 |
        | Directed   | Yes       | Same as the union of `inneighbor` and `outneighbor`. |
        | Weighted   | Yes       | Weights are ignored.                            |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, where
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ... )
        >>>
        >>> # 3. Select the IDs from the neighbor relationship and inspect
        >>> u, v = Node.ref("u"), Node.ref("v")
        >>> neighbor = graph.neighbor()
        >>> select(u.id, v.id).where(neighbor(u, v)).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   1    2
        1   2    1
        2   2    3
        3   2    4
        4   3    2
        5   3    3
        6   4    2

        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute neighbors of
        >>> # Define a subset containing only nodes 2 and 3
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>>
        >>> # Get neighbors only of nodes in the subset
        >>> constrained_neighbor = graph.neighbor(of=subset)
        >>> select(u.id, v.id).where(constrained_neighbor(u, v)).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   2    1
        1   2    3
        2   2    4
        3   3    2
        4   3    3

        Notes
        -----
        The ``neighbor()`` method, called with no parameters, computes and caches
        the full neighbor relationship, providing efficient reuse across multiple
        calls to ``neighbor()``. In contrast, ``neighbor(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the neighbor relation is needed
        across a program, ``neighbor()`` is typically more efficient; this is the
        typical case. Use ``neighbor(of=subset)`` only when small subsets of the
        neighbor relationship are needed collectively across the program.

        See Also
        --------
        inneighbor
        outneighbor

        """
        if of is None:
            return self._neighbor
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._neighbor_of(of)

    def _validate_node_subset_parameter(self, of_relation):
        """
        Validate that a parameter identifying a subset of nodes of interest is
        is a unary relationship containing nodes that is attached to
        the same model that the graph is attached to.
        """
        # Validate that the parameter is a relationship.
        assert isinstance(of_relation, Relationship), (
            "The 'of' parameter must be a `Relationship`, "
            f"but is a `{type(of_relation).__name__}`."
        )

        # Validate that the relationship is attached to the same model as the graph.
        assert of_relation._model is self._model, (
            "The given 'of' relationship must be attached to the same model as the graph."
        )

        # Validate that it's a unary relationship (has exactly one field).
        assert len(of_relation._fields) == 1, (
            "The 'of' parameter must be a unary relationship, "
            f"but it has {len(of_relation._fields)} fields."
        )

        # Validate that the concept type matches the graph's Node concept.
        assert of_relation._fields[0].type_str == self.Node._name, (
            f"The 'of' relationship must be over the graph's Node concept ('{self.Node._name}'), "
            f"but is over '{of_relation._fields[0].type_str}'."
        )

    @cached_property
    def _neighbor(self):
        """Lazily define and cache the self._neighbor relationship."""
        return self._create_neighbor_relationship(nodes_subset=None)

    def _neighbor_of(self, nodes_subset: Relationship):
        """
        Create a neighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_neighbor_relationship(nodes_subset=nodes_subset)

    def _create_neighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _neighbor_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has neighbor {{dst:{self._NodeConceptStr}}}")
        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            # If the graph is directed, the _edge relation is not symmetric,
            # requiring separate rules to capture out-neighbors and in-neighbors.
            #
            # Capture out-neighbors.
            where(
                self._edge(src, dst),
                *([nodes_subset(src)] if nodes_subset else [])
            ).define(
                _neighbor_rel(src, dst)
            )
            # Capture in-neighbors.
            where(
                self._edge(src, dst),
                *([nodes_subset(dst)] if nodes_subset else [])
            ).define(
                _neighbor_rel(dst, src)
            )
        elif not self.directed:
            # If the graph is undirected, the _edge relation is symmetric,
            # so a single rule suffices to capture all neighbors.
            where(
                self._edge(src, dst),
                *([nodes_subset(src)] if nodes_subset else [])
            ).define(
                _neighbor_rel(src, dst)
            )

        return _neighbor_rel


    @include_in_docs
    def inneighbor(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship of all nodes and their in-neighbors.

        An in-neighbor of a node `u` is any node `v` where an edge from `v`
        to `u` exists. For undirected graphs, this is identical to `neighbor`.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the inneighbor computation: only
            in-neighbors of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a destination node
            and one of its in-neighbors.

        Relationship Schema
        -------------------
        ``inneighbor(node, inneighbor_node)``

        * **node** (*Node*): The destination node.
        * **inneighbor_node** (*Node*): The in-neighbor of the node (i.e., the source of an incoming edge).

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes               |
        | :--------- | :-------- | :------------------ |
        | Undirected | Yes       | Same as `neighbor`. |
        | Directed   | Yes       |                     |
        | Weighted   | Yes       | Weights are ignored.|

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, where
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ... )
        >>>
        >>> # 3. Select the IDs from the in-neighbor relationship and inspect
        >>> node, inneighbor_node = Node.ref("node"), Node.ref("inneighbor_node")
        >>> inneighbor = graph.inneighbor()
        >>> select(
        ...     node.id,
        ...     inneighbor_node.id
        ... ).where(
        ...     inneighbor(node, inneighbor_node)
        ... ).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   2    1
        1   3    2
        2   3    3
        3   4    2

        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute in-neighbors of
        >>> # Define a subset containing only nodes 2 and 3
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>>
        >>> # Get in-neighbors only of nodes in the subset
        >>> constrained_inneighbor = graph.inneighbor(of=subset)
        >>> select(node.id, inneighbor_node.id).where(constrained_inneighbor(node, inneighbor_node)).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   2    1
        1   3    2
        2   3    3

        Notes
        -----
        The ``inneighbor()`` method, called with no parameters, computes and caches
        the full inneighbor relationship, providing efficient reuse across multiple
        calls to ``inneighbor()``. In contrast, ``inneighbor(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the inneighbor relation is needed
        across a program, ``inneighbor()`` is typically more efficient; this is the
        typical case. Use ``inneighbor(of=subset)`` only when small subsets of the
        inneighbor relationship are needed collectively across the program.

        See Also
        --------
        neighbor
        outneighbor

        """
        if of is None:
            return self._inneighbor
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._inneighbor_of(of)

    @cached_property
    def _inneighbor(self):
        """Lazily define and cache the self._inneighbor relationship."""
        return self._create_inneighbor_relationship(nodes_subset=None)

    def _inneighbor_of(self, nodes_subset: Relationship):
        """
        Create an inneighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_inneighbor_relationship(nodes_subset=nodes_subset)

    def _create_inneighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _inneighbor_rel = self._model.Relationship(f"{{dst:{self._NodeConceptStr}}} has inneighbor {{src:{self._NodeConceptStr}}}")
        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            # For directed graphs, in-neighbors are simply source nodes that
            # have an edge to the destination nodes in our subset.
            where(
                self._edge(src, dst),
                *([nodes_subset(dst)] if nodes_subset else [])
            ).define(
                _inneighbor_rel(dst, src)
            )
        elif not self.directed:
            # For undirected graphs, the _edge relation is symmetric,
            # so neighbors and in-neighbors are the same.
            where(
                self._edge(src, dst),
                *([nodes_subset(dst)] if nodes_subset else [])
            ).define(
                _inneighbor_rel(dst, src)
            )
            # TODO: This likely isn't the most efficient way to formulate
            #   this logic, but it's good enough for now.

        return _inneighbor_rel


    @include_in_docs
    def outneighbor(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship of all nodes and their out-neighbors.

        An out-neighbor of a node `u` is any node `v` where an edge from `u`
        to `v` exists. For undirected graphs, this is identical to `neighbor`.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the outneighbor computation: only
            out-neighbors of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a source node
            and one of its out-neighbors.

        Relationship Schema
        -------------------
        ``outneighbor(node, outneighbor_node)``

        * **node** (*Node*): The source node.
        * **outneighbor_node** (*Node*): The out-neighbor of the node (i.e., the destination of an outgoing edge).

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes               |
        | :--------- | :-------- | :------------------ |
        | Undirected | Yes       | Same as `neighbor`. |
        | Directed   | Yes       |                     |
        | Weighted   | Yes       | Weights are ignored.|

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, where
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the IDs from the out-neighbor relationship and inspect
        >>> node, outneighbor_node = Node.ref("node"), Node.ref("outneighbor_node")
        >>> outneighbor = graph.outneighbor()
        >>> select(
        ...     node.id,
        ...     outneighbor_node.id
        ... ).where(
        ...     outneighbor(node, outneighbor_node)
        ... ).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   1    2
        1   2    3
        2   2    4
        3   3    3

        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute out-neighbors of
        >>> # Define a subset containing only nodes 2 and 3
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>>
        >>> # Get out-neighbors only of nodes in the subset
        >>> constrained_outneighbor = graph.outneighbor(of=subset)
        >>> select(node.id, outneighbor_node.id).where(constrained_outneighbor(node, outneighbor_node)).inspect()
        ▰▰▰▰ Setup complete
        id  id2
        0   2    3
        1   2    4
        2   3    3

        Notes
        -----
        The ``outneighbor()`` method, called with no parameters, computes and caches
        the full outneighbor relationship, providing efficient reuse across multiple
        calls to ``outneighbor()``. In contrast, ``outneighbor(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the outneighbor relation is needed
        across a program, ``outneighbor()`` is typically more efficient; this is the
        typical case. Use ``outneighbor(of=subset)`` only when small subsets of the
        outneighbor relationship are needed collectively across the program.

        See Also
        --------
        neighbor
        inneighbor

        """
        if of is None:
            return self._outneighbor
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._outneighbor_of(of)

    @cached_property
    def _outneighbor(self):
        """Lazily define and cache the self._outneighbor relationship."""
        return self._create_outneighbor_relationship(nodes_subset=None)

    def _outneighbor_of(self, nodes_subset: Relationship):
        """
        Create an outneighbor relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_outneighbor_relationship(nodes_subset=nodes_subset)

    def _create_outneighbor_relationship(self, *, nodes_subset: Optional[Relationship]):
        _outneighbor_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has outneighbor {{dst:{self._NodeConceptStr}}}")
        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            # For directed graphs, out-neighbors are simply destination nodes that
            # have an edge from the source nodes in our subset.
            where(
                self._edge(src, dst),
                *([nodes_subset(src)] if nodes_subset else [])
            ).define(
                _outneighbor_rel(src, dst)
            )
        elif not self.directed:
            # For undirected graphs, the _edge relation is symmetric,
            # so neighbors and out-neighbors are the same.
            where(
                self._edge(src, dst),
                *([nodes_subset(src)] if nodes_subset else [])
            ).define(
                _outneighbor_rel(src, dst)
            )

        return _outneighbor_rel


    @include_in_docs
    def common_neighbor(self):
        """Returns a ternary relationship of all common neighbor triplets.

        A node `w` is a common neighbor of a pair of nodes `u` and `v` if
        `w` is a neighbor of both `u` and `v`.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and one of their common neighbors.

        Relationship Schema
        -------------------
        ``common_neighbor(node_u, node_v, common_neighbor_node)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **common_neighbor_node** (*Node*): The common neighbor of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>>
        >>> # 3. Select the IDs from the common_neighbor relationship and inspect
        >>> u, v, w = Node.ref("u"), Node.ref("v"), Node.ref("w")
        >>> common_neighbor = graph.common_neighbor()
        >>> select(
        ...     u.id, v.id, w.id
        ... ).where(
        ...     common_neighbor(u, v, w)
        ... ).inspect()
        ▰▰▰▰ Setup complete
            id  id2  id3
        0    1    1    2
        1    1    3    2
        2    1    4    2
        3    2    2    1
        4    2    2    3
        5    2    2    4
        6    2    3    3
        7    2    3    4
        8    2    4    3
        9    3    1    2
        10   3    2    3
        11   3    2    4
        12   3    3    2
        13   3    3    3
        14   3    3    4
        15   3    4    2
        16   3    4    3
        17   4    1    2
        18   4    2    3
        19   4    3    2
        20   4    3    3
        21   4    4    2
        22   4    4    3

        """
        warnings.warn(
            (
                "`common_neighbor` presently always computes common neighbors "
                "for all pairs of nodes in the graph. To provide better control "
                "over the computed subset, `common_neighbor`'s interface "
                "will soon need to change."
            ),
            FutureWarning,
            stacklevel=2
        )
        return self._common_neighbor

    @cached_property
    def _common_neighbor(self):
        """Lazily define and cache the self._common_neighbor relationship."""
        _common_neighbor_rel = self._model.Relationship(f"{{node_a:{self._NodeConceptStr}}} and {{node_b:{self._NodeConceptStr}}} have common neighbor {{node_c:{self._NodeConceptStr}}}")
        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._neighbor(node_a, node_c), self._neighbor(node_b, node_c)).define(_common_neighbor_rel(node_a, node_b, node_c))
        return _common_neighbor_rel


    @include_in_docs
    def degree(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship containing the degree of each node.

        For directed graphs, a node's degree is the sum of its indegree and
        outdegree.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the degree computation: only
            degrees of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            degree.

        Relationship Schema
        -------------------
        ``degree(node, node_degree)``

        * **node** (*Node*): The node.
        * **node_degree** (*Integer*): The degree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select, where
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the degree of each node and inspect
        >>> node, node_degree = Node.ref("node"), Integer.ref("node_degree")
        >>> degree = graph.degree()
        >>> select(node.id, node_degree).where(degree(node, node_degree)).inspect()
        ▰▰▰▰ Setup complete
           id  node_degree
        0   1            1
        1   2            3
        2   3            2
        3   4            1

        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute degree of
        >>> # Define a subset containing only nodes 2 and 3
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>>
        >>> # Get degrees only of nodes in the subset
        >>> constrained_degree = graph.degree(of=subset)
        >>> select(node.id, node_degree).where(constrained_degree(node, node_degree)).inspect()
        ▰▰▰▰ Setup complete
           id  node_degree
        0   2            3
        1   3            2

        **Directed Graph Example**

        >>> from relationalai.semantics import define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the degree of each node and inspect
        >>> node, node_degree = Node.ref("node"), Integer.ref("node_degree")
        >>> degree = graph.degree()
        >>> select(node.id, node_degree).where(degree(node, node_degree)).inspect()
        ▰▰▰▰ Setup complete
           id  node_degree
        0   1            1
        1   2            3
        2   3            3
        3   4            1

        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute degree of
        >>> # Define a subset containing only nodes 1 and 4
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 1, node.id == 4)).define(subset(node))
        >>>
        >>> # Get degrees only of nodes in the subset
        >>> constrained_degree = graph.degree(of=subset)
        >>> select(node.id, node_degree).where(constrained_degree(node, node_degree)).inspect()
        ▰▰▰▰ Setup complete
           id  node_degree
        0   1            1
        1   4            1

        Notes
        -----
        The ``degree()`` method, called with no parameters, computes and caches
        the full degree relationship, providing efficient reuse across multiple
        calls to ``degree()``. In contrast, ``degree(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the degree relation is needed
        across a program, ``degree()`` is typically more efficient; this is the
        typical case. Use ``degree(of=subset)`` only when small subsets of the
        degree relationship are needed collectively across the program.

        See Also
        --------
        indegree
        outdegree

        """
        if of is None:
            return self._degree
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._degree_of(of)

    @cached_property
    def _degree(self):
        """Lazily define and cache the self._degree relationship."""
        return self._create_degree_relationship(nodes_subset=None)

    def _degree_of(self, nodes_subset: Relationship):
        """
        Create a degree relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_degree_relationship(nodes_subset=nodes_subset)

    def _create_degree_relationship(self, *, nodes_subset: Optional[Relationship]):
        _degree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has degree {{count:Integer}}")

        if self.directed:
            # For directed graphs, degree is the sum of indegree and outdegree.
            if nodes_subset is None:
                indegree_rel = self._indegree
                outdegree_rel = self._outdegree
            else:
                indegree_rel = self._indegree_of(nodes_subset)
                outdegree_rel = self._outdegree_of(nodes_subset)

            incount, outcount = Integer.ref(), Integer.ref()
            where(
                indegree_rel(self.Node, incount),
                outdegree_rel(self.Node, outcount),
            ).define(_degree_rel(self.Node, incount + outcount))
        else:
            # For undirected graphs, degree is the count of neighbors.
            if nodes_subset is None:
                node_set = self.Node
                count_neighbor_rel = self._count_neighbor
            else:
                node_set = nodes_subset
                count_neighbor_rel = self._count_neighbor_of(nodes_subset)

            where(
                node_set(self.Node), # Necessary given the match on the following line.
                _degree := where(count_neighbor_rel(self.Node, Integer)).select(Integer) | 0,
            ).define(_degree_rel(self.Node, _degree))

        return _degree_rel


    @include_in_docs
    def indegree(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship containing the indegree of each node.

        A node's indegree is the number of incoming edges. For undirected
        graphs, a node's indegree is identical to its degree.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the indegree computation: only
            indegrees of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            indegree.

        Relationship Schema
        -------------------
        ``indegree(node, node_indegree)``

        * **node** (*Node*): The node.
        * **node_indegree** (*Integer*): The indegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                   |
        | :--------- | :-------- | :---------------------- |
        | Undirected | Yes       | Identical to `degree`.  |
        | Directed   | Yes       |                         |
        | Weighted   | Yes       | Weights are ignored.    |

        Examples
        --------
        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select, where, union, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n3, dst=n4),
        ... )
        >>> # 3. Select the indegree of each node and inspect
        >>> node, node_indegree = Node.ref("node"), Integer.ref("node_indegree")
        >>> indegree = graph.indegree()
        >>> select(node.id, node_indegree).where(indegree(node, node_indegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_indegree
        0   1              1
        1   2              2
        2   3              3
        3   4              1
        >>>
        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute indegree of
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>> constrained_indegree = graph.indegree(of=subset)
        >>> select(node.id, node_indegree).where(constrained_indegree(node, node_indegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_indegree
        0   2              2
        1   3              3

        **Directed Graph Example**

        >>> from relationalai.semantics import Model, define, select, where, union, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n3, dst=n4)
        ... )
        >>>
        >>> # 3. Select the indegree of each node and inspect
        >>> node, node_indegree = Node.ref("node"), Integer.ref("node_indegree")
        >>> indegree = graph.indegree()
        >>> select(node.id, node_indegree).where(indegree(node, node_indegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_indegree
        0   1              0
        1   2              1
        2   3              2
        3   4              1
        >>>
        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute indegree of
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>> constrained_indegree = graph.indegree(of=subset)
        >>> select(node.id, node_indegree).where(constrained_indegree(node, node_indegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_indegree
        0   2              1
        1   3              2

        Notes
        -----
        The ``indegree()`` method, called with no parameters, computes and caches
        the full indegree relationship, providing efficient reuse across multiple
        calls to ``indegree()``. In contrast, ``indegree(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the indegree relation is needed
        across a program, ``indegree()`` is typically more efficient; this is the
        typical case. Use ``indegree(of=subset)`` only when small subsets of the
        indegree relationship are needed collectively across the program.

        See Also
        --------
        degree
        outdegree

        """
        if of is None:
            return self._indegree
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._indegree_of(of)

    @cached_property
    def _indegree(self):
        """Lazily define and cache the self._indegree relationship."""
        return self._create_indegree_relationship(nodes_subset=None)

    def _indegree_of(self, nodes_subset: Relationship):
        """
        Create an indegree relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_indegree_relationship(nodes_subset=nodes_subset)

    def _create_indegree_relationship(self, *, nodes_subset: Optional[Relationship]):
        _indegree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has indegree {{count:Integer}}")

        # Choose the appropriate count_inneighbor relationship and node set
        if nodes_subset is None:
            # No constraint - use cached count_inneighbor relationship and all nodes
            count_inneighbor_rel = self._count_inneighbor
            node_set = self.Node
        else:
            # Constrained to nodes in the subset - use constrained count_inneighbor relationship
            count_inneighbor_rel = self._count_inneighbor_of(nodes_subset)
            node_set = nodes_subset

        # Apply the same indegree logic for both cases
        where(
            node_set(self.Node),
            _indegree := where(count_inneighbor_rel(self.Node, Integer)).select(Integer) | 0,
        ).define(_indegree_rel(self.Node, _indegree))

        return _indegree_rel


    @include_in_docs
    def outdegree(self, *, of: Optional[Relationship] = None):
        """Returns a binary relationship containing the outdegree of each node.

        A node's outdegree is the number of outgoing edges. For undirected
        graphs, a node's outdegree is identical to its degree.

        Parameters
        ----------
        of : Relationship, optional
            A unary relationship containing a subset of the graph's nodes. When
            provided, constrains the domain of the outdegree computation: only
            outdegrees of nodes in this relationship are computed and returned.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            outdegree.

        Relationship Schema
        -------------------
        ``outdegree(node, node_outdegree)``

        * **node** (*Node*): The node.
        * **node_outdegree** (*Integer*): The outdegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                   |
        | :--------- | :-------- | :---------------------- |
        | Undirected | Yes       | Identical to `degree`.  |
        | Directed   | Yes       |                         |
        | Weighted   | Yes       | Weights are ignored.    |

        Examples
        --------
        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select, where, union, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the outdegree of each node and inspect
        >>> node, node_outdegree = Node.ref("node"), Integer.ref("node_outdegree")
        >>> outdegree = graph.outdegree()
        >>> select(node.id, node_outdegree).where(outdegree(node, node_outdegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_outdegree
        0   1               1
        1   2               3
        2   3               2
        3   4               1
        >>>
        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute outdegree of
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>> constrained_outdegree = graph.outdegree(of=subset)
        >>> select(node.id, node_outdegree).where(constrained_outdegree(node, node_outdegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_outdegree
        0   2               3
        1   3               2

        **Directed Graph Example**

        >>> from relationalai.semantics import Model, define, select, where, union, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the outdegree of each node and inspect
        >>> node, node_outdegree = Node.ref("node"), Integer.ref("node_outdegree")
        >>> outdegree = graph.outdegree()
        >>> select(node.id, node_outdegree).where(outdegree(node, node_outdegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_outdegree
        0   1               1
        1   2               2
        2   3               1
        3   4               0
        >>>
        >>> # 4. Use 'of' parameter to constrain the set of nodes to compute outdegree of
        >>> subset = model.Relationship(f"{{node:{Node}}} is in subset")
        >>> node = Node.ref()
        >>> where(union(node.id == 2, node.id == 3)).define(subset(node))
        >>> constrained_outdegree = graph.outdegree(of=subset)
        >>> select(node.id, node_outdegree).where(constrained_outdegree(node, node_outdegree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_outdegree
        0   2               2
        1   3               1

        Notes
        -----
        The ``outdegree()`` method, called with no parameters, computes and caches
        the full outdegree relationship, providing efficient reuse across multiple
        calls to ``outdegree()``. In contrast, ``outdegree(of=subset)`` computes a
        constrained relationship specific to the passed-in ``subset`` and that
        call site. When a significant fraction of the outdegree relation is needed
        across a program, ``outdegree()`` is typically more efficient; this is the
        typical case. Use ``outdegree(of=subset)`` only when small subsets of the
        outdegree relationship are needed collectively across the program.

        See Also
        --------
        degree
        indegree

        """
        if of is None:
            return self._outdegree
        else:
            # Validate the 'of' parameter
            self._validate_node_subset_parameter(of)
            return self._outdegree_of(of)

    @cached_property
    def _outdegree(self):
        """Lazily define and cache the self._outdegree relationship."""
        return self._create_outdegree_relationship(nodes_subset=None)

    def _outdegree_of(self, nodes_subset: Relationship):
        """
        Create an outdegree relationship constrained to the subset of nodes
        in `nodes_subset`. Note this relationship is not cached; it is
        specific to the callsite.
        """
        return self._create_outdegree_relationship(nodes_subset=nodes_subset)

    def _create_outdegree_relationship(self, *, nodes_subset: Optional[Relationship]):
        _outdegree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has outdegree {{count:Integer}}")

        # Choose the appropriate count_outneighbor relationship and node set
        if nodes_subset is None:
            # No constraint - use cached count_outneighbor relationship and all nodes
            count_outneighbor_rel = self._count_outneighbor
            node_set = self.Node
        else:
            # Constrained to nodes in the subset - use constrained count_outneighbor relationship
            count_outneighbor_rel = self._count_outneighbor_of(nodes_subset)
            node_set = nodes_subset

        # Apply the same outdegree logic for both cases
        where(
            node_set(self.Node),
            _outdegree := where(count_outneighbor_rel(self.Node, Integer)).select(Integer) | 0,
        ).define(_outdegree_rel(self.Node, _outdegree))

        return _outdegree_rel


    @include_in_docs
    def weighted_degree(self):
        """Returns a binary relationship containing the weighted degree of each node.

        A node's weighted degree is the sum of the weights of all edges
        connected to it. For directed graphs, this is the sum of the weights
        of both incoming and outgoing edges. For unweighted graphs, all edge
        weights are considered to be 1.0.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted degree.

        Relationship Schema
        -------------------
        ``weighted_degree(node, node_weighted_degree)``

        * **node** (*Node*): The node.
        * **node_weighted_degree** (*Float*): The weighted degree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                              |
        | :----------- | :-------- | :--------------------------------- |
        | Undirected   | Yes       |                                    |
        | Directed     | Yes       |                                    |
        | Weighted     | Yes       |                                    |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n2, dst=n1, weight=-1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ... )
        >>>
        >>> # 3. Select the weighted degree of each node and inspect
        >>> node, node_weighted_degree = Node.ref("node"), Float.ref("node_weighted_degree")
        >>> weighted_degree = graph.weighted_degree()
        >>> select(node.id, node_weighted_degree).where(weighted_degree(node, node_weighted_degree)).inspect()
        ▰▰▰▰ Setup complete
            id  node_weighted_degree
        0   1                   0.0
        1   2                   1.0
        2   3                   1.0

        See Also
        --------
        weighted_indegree
        weighted_outdegree

        """
        return self._weighted_degree

    @cached_property
    def _weighted_degree(self):
        """Lazily define and cache the self._weighted_degree relationship."""
        _weighted_degree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has weighted degree {{weight:Float}}")

        if self.directed:
            inweight, outweight = Float.ref(), Float.ref()
            where(
                self._weighted_indegree(self.Node, inweight),
                self._weighted_outdegree(self.Node, outweight),
            ).define(_weighted_degree_rel(self.Node, inweight + outweight))
        elif not self.directed:
            dst, weight = self.Node.ref(), Float.ref()
            where(
                self.Node,
                _weighted_degree := sum(dst, weight).per(self.Node).where(self._weight(self.Node, dst, weight)) | 0.0,
            ).define(_weighted_degree_rel(self.Node, _weighted_degree))

        return _weighted_degree_rel


    @include_in_docs
    def weighted_indegree(self):
        """Returns a binary relationship containing the weighted indegree of each node.

        A node's weighted indegree is the sum of the weights of all incoming
        edges. For undirected graphs, this is identical to `weighted_degree`.
        For unweighted graphs, all edge weights are considered to be 1.0.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted indegree.

        Relationship Schema
        -------------------
        ``weighted_indegree(node, node_weighted_indegree)``

        * **node** (*Node*): The node.
        * **node_weighted_indegree** (*Float*): The weighted indegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                                  |
        | :----------- | :-------- | :------------------------------------- |
        | Undirected   | Yes       | Identical to `weighted_degree`.        |
        | Directed     | Yes       |                                        |
        | Weighted     | Yes       |                                        |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n2, dst=n1, weight=-1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ... )
        >>>
        >>> # 3. Select the weighted indegree of each node and inspect
        >>> node, node_weighted_indegree = Node.ref("node"), Float.ref("node_weighted_indegree")
        >>> weighted_indegree = graph.weighted_indegree()
        >>> select(
        ...     node.id, node_weighted_indegree
        ... ).where(
        ...     weighted_indegree(node, node_weighted_indegree)
        ... ).inspect()
        ▰▰▰▰ Setup complete
            id  node_weighted_indegree
        0   1                    -1.0
        1   2                     1.0
        2   3                     1.0

        See Also
        --------
        weighted_degree
        weighted_outdegree

        """
        return self._weighted_indegree

    @cached_property
    def _weighted_indegree(self):
        """Lazily define and cache the self._weighted_indegree relationship."""
        _weighted_indegree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has weighted indegree {{weight:Float}}")

        src, inweight = self.Node.ref(), Float.ref()
        where(
            self.Node,
            _weighted_indegree := sum(src, inweight).per(self.Node).where(self._weight(src, self.Node, inweight)) | 0.0,
        ).define(_weighted_indegree_rel(self.Node, _weighted_indegree))

        return _weighted_indegree_rel


    @include_in_docs
    def weighted_outdegree(self):
        """Returns a binary relationship containing the weighted outdegree of each node.

        A node's weighted outdegree is the sum of the weights of all outgoing
        edges. For undirected graphs, this is identical to `weighted_degree`.
        For unweighted graphs, all edge weights are considered to be 1.0.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            weighted outdegree.

        Relationship Schema
        -------------------
        ``weighted_outdegree(node, node_weighted_outdegree)``

        * **node** (*Node*): The node.
        * **node_weighted_outdegree** (*Float*): The weighted outdegree of the node.

        Supported Graph Types
        ---------------------
        | Graph Type   | Supported | Notes                                  |
        | :----------- | :-------- | :------------------------------------- |
        | Undirected   | Yes       | Identical to `weighted_degree`.        |
        | Directed     | Yes       |                                        |
        | Weighted     | Yes       |                                        |
        | Unweighted   | Yes       | Edge weights are considered to be 1.0. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed, weighted graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n2, dst=n1, weight=-1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ... )
        >>>
        >>> # 3. Select the weighted outdegree of each node and inspect
        >>> node, node_weighted_outdegree = Node.ref("node"), Float.ref("node_weighted_outdegree")
        >>> weighted_outdegree = graph.weighted_outdegree()
        >>> select(
        ...     node.id, node_weighted_outdegree
        ... ).where(
        ...     weighted_outdegree(node, node_weighted_outdegree)
        ... ).inspect()
        ▰▰▰▰ Setup complete
            id  node_weighted_outdegree
        0   1                      1.0
        1   2                      0.0
        2   3                      0.0

        See Also
        --------
        weighted_degree
        weighted_indegree

        """
        return self._weighted_outdegree

    @cached_property
    def _weighted_outdegree(self):
        """Lazily define and cache the self._weighted_outdegree relationship."""
        _weighted_outdegree_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has weighted outdegree {{weight:Float}}")

        dst, outweight = self.Node.ref(), Float.ref()
        where(
            self.Node,
            _weighted_outdegree := sum(dst, outweight).per(self.Node).where(self._weight(self.Node, dst, outweight)) | 0.0,
        ).define(_weighted_outdegree_rel(self.Node, _weighted_outdegree))

        return _weighted_outdegree_rel


    @include_in_docs
    def degree_centrality(self):
        """Returns a binary relationship containing the degree centrality of each node.

        Degree centrality is a measure of a node's importance, defined as its
        degree (or weighted degree for weighted graphs) divided by the number
        of other nodes in the graph. For simple graphs without self-loops, this
        value will be at most 1.0; graphs with self-loops might have nodes
        with a degree centrality greater than 1.0.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            degree centrality.

        Relationship Schema
        -------------------
        ``degree_centrality(node, centrality)``

        * **node** (*Node*): The node.
        * **centrality** (*Float*): The degree centrality of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                         |
        | :--------- | :-------- | :-------------------------------------------- |
        | Undirected | Yes       |                                               |
        | Directed   | Yes       |                                               |
        | Weighted   | Yes       | The calculation uses the node's weighted degree. |

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an unweighted graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ... )
        >>>
        >>> # 3. Select the degree centrality of each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> degree_centrality = graph.degree_centrality()
        >>> select(node.id, centrality).where(degree_centrality(node, centrality)).inspect()
        ▰▰▰▰ Setup complete
           id centrality
        0   1   0.333333
        1   2   1.000000
        2   3   1.000000
        3   4   0.666667

        **Weighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a weighted graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=2.0),
        ...     Edge.new(src=n1, dst=n3, weight=0.5),
        ...     Edge.new(src=n2, dst=n3, weight=1.5),
        ... )
        >>>
        >>> # 3. Select the degree centrality using weighted degrees
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> degree_centrality = graph.degree_centrality()
        >>> select(node.id, centrality).where(degree_centrality(node, centrality)).inspect()
        ▰▰▰▰ Setup complete
            id  centrality
        0   1        1.25
        1   2        1.75
        2   3        1.00

        See Also
        --------
        degree
        weighted_degree

        """
        return self._degree_centrality

    @cached_property
    def _degree_centrality(self):
        """Lazily define and cache the self._degree_centrality relationship."""
        _degree_centrality_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has {{degree_centrality:Float}}")

        degree = Integer.ref()
        weighted_degree = Float.ref()

        # TODO: Collapse the logic for these edge cases using a match.

        # A single isolated node has degree centrality zero.
        where(
            self._num_nodes(1),
            self._degree(self.Node, 0)
        ).define(_degree_centrality_rel(self.Node, 0.0))

        # A single non-isolated node has degree centrality one.
        where(
            self._num_nodes(1),
            self._degree(self.Node, degree),
            degree > 0
        ).define(_degree_centrality_rel(self.Node, 1.0))

        # General case, i.e. with more than one node.
        num_nodes = Integer.ref()
        if self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._weighted_degree(self.Node, weighted_degree)
            ).define(_degree_centrality_rel(self.Node, weighted_degree / (num_nodes - 1.0)))
        elif not self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._degree(self.Node, degree)
            ).define(_degree_centrality_rel(self.Node, degree / (num_nodes - 1.0)))
            # TODO: .to_df() second-column dtype becomes `object` rather than `Float`.

        return _degree_centrality_rel


    def eigenvector_centrality(self):
        """Returns a binary relationship containing the eigenvector centrality of each node.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            eigenvector centrality.

        Relationship Schema
        -------------------
        ``eigenvector_centrality(node, centrality)``

        * **node** (*Node*): The node.
        * **centrality** (*Float*): The eigenvector centrality of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                     |
        | :--------- | :-------- | :---------------------------------------- |
        | Undirected | Yes       | See Notes for convergence criteria.       |
        | Directed   | No        | Will not converge.                        |
        | Weighted   | Yes       | Assumes non-negative weights.             |

        Notes
        -----
        Eigenvector centrality is a measure of the centrality or importance
        of a node in a graph based on finding the eigenvector associated
        with the top eigenvalue of the adjacency matrix. We use the power
        method to compute the eigenvector in our implementation. Note that
        the power method `requires the adjacency matrix to be diagonalizable <https://en.wikipedia.org/wiki/Power_iteration>`_
        and will only converge if the absolute value of the top 2
        eigenvalues is distinct. Thus, if the graph you are using has an
        adjacency matrix that is not diagonalizable or the top two
        eigenvalues are not distinct, this method will not converge.

        In the case of weighted graphs, weights are assumed to be non-negative.

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an unweighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n4)
        ... )
        >>>
        >>> # 3. Select the eigenvector centrality for each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> eigenvector_centrality = graph.eigenvector_centrality()
        >>> select(node.id, centrality).where(eigenvector_centrality(node, centrality)).inspect()
        # The output will show the resulting scores, for instance:
        # (1, 0.3717480344601844)
        # (2, 0.6015009550075456)
        # (3, 0.6015009550075456)
        # (4, 0.3717480344601844)

        **Weighted Graph Example**

        >>> # 1. Set up a weighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=0.8),
        ...     Edge.new(src=n2, dst=n3, weight=0.7),
        ...     Edge.new(src=n3, dst=n3, weight=2.0),
        ...     Edge.new(src=n2, dst=n4, weight=1.5)
        ... )
        >>>
        >>> # 3. Select the eigenvector centrality for each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> eigenvector_centrality = graph.eigenvector_centrality()
        >>> select(node.id, centrality).where(eigenvector_centrality(node, centrality)).inspect()
        # The output will show the resulting scores, for instance:
        # (1, 0.15732673092171892)
        # (2, 0.4732508189314368)
        # (3, 0.8150240891426493)
        # (4, 0.2949876204782229)

        """
        raise NotImplementedError("`eigenvector_centrality` is not yet implemented")

    def betweenness_centrality(self):
        """Returns a binary relationship containing the betweenness centrality of each node.

        Betweenness centrality measures how important a node is based on how many times that
        node appears in a shortest path between any two nodes in the graph. Nodes with high
        betweenness centrality represent bridges between different parts of the graph. For
        example, in a network representing airports and flights between them, nodes with high
        betweenness centrality may identify "hub" airports that connect flights to different
        regions.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            betweenness centrality.

        Relationship Schema
        -------------------
        ``betweenness_centrality(node, centrality)``

        * **node** (*Node*): The node.
        * **centrality** (*Float*): The betweenness centrality of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----

        Calculating betweenness centrality involves computing all of the shortest paths between
        every pair of nodes in a graph and can be expensive to calculate exactly. The
        `betweenness_centrality` relation gives an approximation using the
        [Brandes-Pich](https://www.worldscientific.com/doi/abs/10.1142/S0218127407018403)
        algorithm, which samples nodes uniformly at random and performs single-source
        shortest-path computations from those nodes.

        This implementation nominally samples 100 nodes, yielding time complexity of
        `100 * O(|V|+|E|))`. If the graph has fewer than 100 nodes, it reduces to the
        [Brandes algorithm](http://snap.stanford.edu/class/cs224w-readings/brandes01centrality.pdf),
        with time complexity `O(|V|(|V|+|E|))` for unweighted graphs.

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Select the betweenness centrality for each node and inspect
        >>> node, centrality = Node.ref("node"), Float.ref("centrality")
        >>> betweenness_centrality = graph.betweenness_centrality()
        >>> select(node.id, centrality).where(betweenness_centrality(node, centrality)).inspect()
        # The output will show the resulting scores, for instance:
        # (1, 0.0)
        # (2, 3.0)
        # (3, 0.0)
        # (4, 0.0)

        """
        raise NotImplementedError("`betweenness_centrality` is not implemented.")

    def pagerank(
            self,
            damping_factor:float = 0.85,
            tolerance:float = 1e-6,
            max_iter:int = 20,
    ):
        """Returns a binary relationship containing the PageRank score of each node.

        Parameters
        ----------
        damping_factor : float, optional
            The damping factor for the PageRank calculation. Must be in the
            range [0, 1). Default is 0.85.
        tolerance : float, optional
            The convergence tolerance for the PageRank calculation. Must be
            a non-negative float. Default is 1e-6.
        max_iter : int, optional
            The maximum number of iterations for PageRank to run. Must be a
            positive integer. Default is 20.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            PageRank score.

        Relationship Schema
        -------------------
        ``pagerank(node, score)``

        * **node** (*Node*): The node.
        * **score** (*Float*): The PageRank score of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                              |
        | :--------- | :-------- | :--------------------------------- |
        | Undirected | Yes       |                                    |
        | Directed   | Yes       |                                    |
        | Weighted   | Yes       | Only non-negative weights supported. |
        | Unweighted | Yes       |                                    |

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an unweighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4)
        ... )
        >>>
        >>> # 3. Compute PageRank with default parameters and inspect
        >>> node, score = Node.ref("node"), Float.ref("score")
        >>> pagerank = graph.pagerank()
        >>> select(node.id, score).where(pagerank(node, score)).inspect()
        # The output will show the PageRank score for each node:
        # (1, 0.155788...)
        # (2, 0.417487...)
        # (3, 0.270935...)
        # (4, 0.155788...)

        **Weighted Graph Example with Configuration**

        >>> # 1. Set up a weighted, directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n1, dst=n3, weight=2.0),
        ...     Edge.new(src=n3, dst=n4, weight=3.0)
        ... )
        >>>
        >>> # 3. Compute PageRank with custom parameters and inspect
        >>> node, score = Node.ref("node"), Float.ref("score")
        >>> pagerank = graph.pagerank(damping_factor=0.85, tolerance=1e-6, max_iter=20)
        >>> select(node.id, score).where(pagerank(node, score)).inspect()
        # The output will show the PageRank score for each node:
        # (1, 0.264904)
        # (2, 0.112556)
        # (3, 0.387444)
        # (4, 0.235096)

        **Example with Diagnostics (Hypothetical)**

        The following example is hypothetical, and requires replacement
        once this method is implemented in full, illustrating however
        the implemented diagnostics mechanism works.

        >>> # 1. Set up graph as above
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n1, dst=n3, weight=2.0),
        ...     Edge.new(src=n3, dst=n4, weight=3.0)
        ... )
        >>>
        >>> # 2. Hypothetical call to get results and diagnostics
        >>> pagerank_info = graph.pagerank(diagnostics=True)
        >>>
        >>> # 3. Select the results
        >>> # select(pagerank_info.result).inspect()
        # The output would show the PageRank scores:
        # (1, 0.161769)
        # (2, 0.207603)
        # (3, 0.253438)
        # (4, 0.377191)
        >>>
        >>> # 4. Select the number of iterations from diagnostics
        >>> # select(pagerank_info.diagnostics.num_iterations).inspect()
        # The output would show the number of iterations:
        # 13
        >>>
        >>> # 5. Select the termination status from diagnostics
        >>> # select(pagerank_info.diagnostics.termination_status).inspect()
        # The output would show the termination status:
        # :converged

        """
        _assert_type("pagerank:tolerance", tolerance, Real)
        _assert_exclusive_lower_bound("pagerank:tolerance", tolerance, 0.0)

        _assert_type("pagerank:max_iter", max_iter, int)
        _assert_exclusive_lower_bound("pagerank:max_iter", max_iter, 0)

        _assert_type("pagerank:damping_factor", damping_factor, Real)
        _assert_inclusive_lower_bound("pagerank:damping_factor", damping_factor, 0.0)
        _assert_exclusive_upper_bound("pagerank:damping_factor", damping_factor, 1.0)

        raise NotImplementedError("`pagerank` is not yet implemented.")


    @include_in_docs
    def triangle(self):
        """Returns a ternary relationship containing all triangles in the graph.

        Unlike `unique_triangle`, this relationship contains all permutations
        of the nodes for each triangle found.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a triangle.

        Relationship Schema
        -------------------
        ``triangle(node_a, node_b, node_c)``

        * **node_a** (*Node*): The first node in the triangle.
        * **node_b** (*Node*): The second node in the triangle.
        * **node_c** (*Node*): The third node in the triangle.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        **Directed Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph with a 3-cycle
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n1),
        ... )
        >>>
        >>> # 3. Select all triangles and inspect
        >>> a,b,c = Node.ref("a"), Node.ref("b"), Node.ref("c")
        >>> triangle = graph.triangle()
        >>> select(a.id, b.id, c.id).where(triangle(a, b, c)).inspect()
        ▰▰▰▰ Setup complete
           id  id2  id3
        0   1    2    3
        1   2    3    1
        2   3    1    2

        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph with a triangle
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n1),
        ... )
        >>>
        >>> # 3. Select all triangles and inspect
        >>> a,b,c = Node.ref("a"), Node.ref("b"), Node.ref("c")
        >>> triangle = graph.triangle()
        >>> select(a.id, b.id, c.id).where(triangle(a, b, c)).inspect()
        ▰▰▰▰ Setup complete
           id  id2  id3
        0   1    2    3
        1   1    3    2
        2   2    1    3
        3   2    3    1
        4   3    1    2
        5   3    2    1

        See Also
        --------
        unique_triangle
        num_triangles
        triangle_count

        """
        warnings.warn(
            (
                "`triangle` presently always computes all triangles "
                "in the graph. To provide better control over the computed subset, "
                "`triangle`'s interface may soon change."
            ),
            FutureWarning,
            stacklevel=2
        )
        return self._triangle

    @cached_property
    def _triangle(self):
        """Lazily define and cache the self._triangle relationship."""
        _triangle_rel = self._model.Relationship(f"{{node_a:{self._NodeConceptStr}}} and {{node_b:{self._NodeConceptStr}}} and {{node_c:{self._NodeConceptStr}}} form a triangle")

        a, b, c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        if self.directed:
            where(self._unique_triangle(a, b, c)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(b, c, a)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(c, a, b)).define(_triangle_rel(a, b, c))
        else:
            where(self._unique_triangle(a, b, c)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(a, c, b)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(b, a, c)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(b, c, a)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(c, a, b)).define(_triangle_rel(a, b, c))
            where(self._unique_triangle(c, b, a)).define(_triangle_rel(a, b, c))

        return _triangle_rel


    @include_in_docs
    def unique_triangle(self):
        """Returns a ternary relationship containing all unique triangles in the graph.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a unique
            triangle.

        Relationship Schema
        -------------------
        ``unique_triangle(node_a, node_b, node_c)``

        * **node_a** (*Node*): The first node in the triangle.
        * **node_b** (*Node*): The second node in the triangle.
        * **node_c** (*Node*): The third node in the triangle.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        This relationship contains triples of nodes `(a, b, c)` representing
        unique triangles.

        For **undirected graphs**, uniqueness of each triangle is guaranteed
        because the relationship only contains triples where `a < b < c`.

        For **directed graphs**, the triple `(a, b, c)` represents a triangle
        with directed edges `(a, b)`, `(b, c)`, and `(c, a)`, and is unique up
        to ordering of the nodes and direction of the edges. `unique_triangle`
        only contains triples such that `a < b`, `a < c`, and `b != c`. For
        example, the triples `(1, 2, 3)` and `(1, 3, 2)` represent two unique
        directed triangles.

        Examples
        --------
        **Directed Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n3),
        ...     Edge.new(src=n2, dst=n1),
        ...     Edge.new(src=n3, dst=n2),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n2, dst=n4),
        ... )
        >>>
        >>> # 3. Select the unique triangles and inspect
        >>> a,b,c = Node.ref("a"), Node.ref("b"), Node.ref("c")
        >>> unique_triangle = graph.unique_triangle()
        >>> select(a.id, b.id, c.id).where(unique_triangle(a, b, c)).inspect()
        ▰▰▰▰ Setup complete
           id  id2  id3
        0   1    3    2

        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges forming two triangles
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n1), # Forms triangle (1,2,3)
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n3, dst=n4),  # Forms triangle (2,3,4)
        ... )
        >>>
        >>> # 3. Select the unique triangles and inspect
        >>> a,b,c = Node.ref("a"), Node.ref("b"), Node.ref("c")
        >>> unique_triangle = graph.unique_triangle()
        >>> select(a.id, b.id, c.id).where(unique_triangle(a, b, c)).inspect()
        ▰▰▰▰ Setup complete
           id  id2  id3
        0   1    2    3
        1   2    3    4

        See Also
        --------
        triangle
        num_triangles
        triangle_count

        """
        warnings.warn(
            (
                "`unique_triangle` presently always computes all unique triangles "
                "in the graph. To provide better control over the computed subset, "
                "`unique_triangle`'s interface may soon change."
            ),
            FutureWarning,
            stacklevel=2
        )
        return self._unique_triangle

    @cached_property
    def _unique_triangle(self):
        """Lazily define and cache the self._unique_triangle relationship."""
        _unique_triangle_rel = self._model.Relationship(f"{{node_a:{self._NodeConceptStr}}} and {{node_b:{self._NodeConceptStr}}} and {{node_c:{self._NodeConceptStr}}} form unique triangle")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            self._unique_triangle_fragment(node_a, node_b, node_c)
        ).define(_unique_triangle_rel(node_a, node_b, node_c))

        return _unique_triangle_rel

    def _unique_triangle_fragment(self, node_a, node_b, node_c):
        """
        Helper function that returns a fragment, specifically a where clause
        constraining the given triplet of nodes to unique triangles in the graph.
        """
        if self.directed:
            return where(
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node_b, node_c),
                self._reversed_oriented_edge(node_c, node_a)
            )
        else:
            return where(
                self._oriented_edge(node_a, node_b),
                self._oriented_edge(node_b, node_c),
                self._oriented_edge(node_a, node_c)
            )

    @cached_property
    def _no_loop_edge(self):
        """Lazily define and cache the self._no_loop_edge (helper, non-public) relationship."""
        _no_loop_edge_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has nonloop edge to {{dst:{self._NodeConceptStr}}}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src != dst
        ).define(_no_loop_edge_rel(src, dst))

        return _no_loop_edge_rel

    @cached_property
    def _oriented_edge(self):
        """Lazily define and cache the self._oriented_edge (helper, non-public) relationship."""
        _oriented_edge_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has oriented edge to {{dst:{self._NodeConceptStr}}}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src < dst
        ).define(_oriented_edge_rel(src, dst))

        return _oriented_edge_rel

    @cached_property
    def _reversed_oriented_edge(self):
        """Lazily define and cache the self._reversed_oriented_edge (helper, non-public) relationship."""
        _reversed_oriented_edge_rel = self._model.Relationship(f"{{src:{self._NodeConceptStr}}} has reversed oriented edge to {{dst:{self._NodeConceptStr}}}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src > dst
        ).define(_reversed_oriented_edge_rel(src, dst))

        return _reversed_oriented_edge_rel


    @include_in_docs
    def num_triangles(self):
        """Returns a unary relationship containing the total number of unique triangles in the graph.

        This method counts the number of unique triangles as defined by the
        `unique_triangle` relationship, which has different uniqueness
        constraints for directed and undirected graphs.

        Returns
        -------
        Relationship
            A unary relationship containing the total number of unique
            triangles in the graph.

        Relationship Schema
        -------------------
        ``num_triangles(count)``

        * **count** (*Integer*): The total number of unique triangles in the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n3),
        ...     Edge.new(src=n2, dst=n1),
        ...     Edge.new(src=n3, dst=n2),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n1, dst=n4),
        ... )
        >>>
        >>> # 3. Inspect the number of unique triangles
        >>> graph.num_triangles().inspect()
        ▰▰▰▰ Setup complete
           int
        0    1

        See Also
        --------
        triangle
        unique_triangle
        triangle_count

        """
        return self._num_triangles

    @cached_property
    def _num_triangles(self):
        """Lazily define and cache the self._num_triangles relationship."""
        _num_triangles_rel = self._model.Relationship("The graph has {num_triangles:Integer} triangles")

        _num_triangles = Integer.ref()
        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            _num_triangles := count(
                node_a, node_b, node_c
            ).where(
                self._unique_triangle_fragment(node_a, node_b, node_c)
            ) | 0,
        ).define(_num_triangles_rel(_num_triangles))

        return _num_triangles_rel


    @include_in_docs
    def triangle_count(self):
        """Returns a binary relationship containing the number of unique triangles each node belongs to.

        A triangle is a set of three nodes where each node has a directed
        or undirected edge to the other two nodes, forming a 3-cycle.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and the
            number of unique triangles it is a part of.

        Relationship Schema
        -------------------
        ``triangle_count(node, count)``

        * **node** (*Node*): The node.
        * **count** (*Integer*): The number of unique triangles the node belongs to.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n3, dst=n1),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n5, dst=n1),
        ... )
        >>>
        >>> # 3. Select the triangle count for each node and inspect
        >>> node, count = Node.ref("node"), Integer.ref("count")
        >>> triangle_count = graph.triangle_count()
        >>> select(node.id, count).where(triangle_count(node, count)).inspect()
        ▰▰▰▰ Setup complete
           id  count
        0   1      1
        1   2      1
        2   3      1
        3   4      0
        4   5      0

        See Also
        --------
        triangle
        unique_triangle
        num_triangles

        """
        return self._triangle_count

    @cached_property
    def _triangle_count(self):
        """Lazily define and cache the self._triangle_count relationship."""
        _triangle_count_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} belongs to {{count:Integer}} triangles")

        where(
            self.Node,
            _count := self._nonzero_triangle_count_fragment(self.Node) | 0
        ).define(_triangle_count_rel(self.Node, _count))

        return _triangle_count_rel

    def _nonzero_triangle_count_fragment(self, node):
        """
        Helper function that returns a fragment, specifically a count
        of the number of triangles containing the given node.
        """
        node_a, node_b = self.Node.ref(), self.Node.ref()

        if self.directed:
            # For directed graphs, count triangles with any circulation.
            # For example, count both (1-2-3-1) and (1-3-2-1) as triangles.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._no_loop_edge(node_a, node_b),
                self._no_loop_edge(node_b, node)
            )
        else:
            # For undirected graphs, count triangles with a specific circulation.
            # For example, count (1-2-3-1) but not (1-3-2-1) as a triangle.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node, node_b)
            )


    def triangle_community(self):
        """Returns a binary relationship that partitions nodes into communities based on the graph's triangle structure.

        This method finds K-clique communities (with K=3) using the
        percolation method.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            community assignment.

        Relationship Schema
        -------------------
        ``triangle_community(node, community_label)``

        * **node** (*Node*): The node.
        * **community_label** (*Integer*): The node's community assignment.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | No        |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        This method finds K-clique communities (with `K = 3`) using the
        `percolation method <https://en.wikipedia.org/wiki/Clique_percolation_method>`_.
        A triangle community is the union of nodes of all triangles that can
        be reached from one another by adjacent triangles---that is,
        triangles that share exactly two nodes.

        For a given undirected graph `G`, the algorithm works as follows:
        First, all triangles in `G` are enumerated and assigned a unique
        label, each of which becomes a node in a new graph called the
        **clique-graph** of `G`, where two nodes in this new graph are
        connected by an edge if the corresponding triangles share exactly two
        nodes, i.e., the corresponding triangles are adjacent in `G`. Next,
        the connected components of the clique-graph of `G` are computed and
        then assigned community labels. Finally, each node in the original
        graph is assigned the community label of the triangle to which it
        belongs. Nodes that are not contained in any triangle are not
        assigned a community label. This algorithm is not supported for
        directed graphs since adjacency is not defined for directed
        triangles.

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n1, dst=n3),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n4, dst=n5),
        ...     Edge.new(src=n4, dst=n6),
        ...     Edge.new(src=n5, dst=n6)
        ... )
        >>>
        >>> # 3. Select the community label for each node and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> triangle_community = graph.triangle_community()
        >>> select(node.id, label).where(triangle_community(node, label)).inspect()
        # The output will show each node in a triangle mapped to a community:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        """
        raise NotImplementedError("`triangle_community` is not yet implemented")


    @include_in_docs
    def local_clustering_coefficient(self):
        """Returns a binary relationship containing the local clustering coefficient of each node.

        The local clustering coefficient quantifies how close a node's neighbors
        are to forming a clique (a complete subgraph). The coefficient ranges
        from 0.0 to 1.0, where 0.0 indicates none of the neighbors have edges
        directly connecting them, and 1.0 indicates all neighbors have edges
        directly connecting them.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            local clustering coefficient.

        Raises
        ------
        NotImplementedError
            If the graph is directed.

        Relationship Schema
        -------------------
        ``local_clustering_coefficient(node, coefficient)``

        * **node** (*Node*): The node.
        * **coefficient** (*Float*): The local clustering coefficient of the node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes              |
        | :--------- | :-------- | :----------------- |
        | Undirected | Yes       |                    |
        | Directed   | No        | Undirected only.   |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        The formal definition of the local clustering coefficient (`C`) for a
        node (`v`) can be given as::

            C(v) = (2 * num_edges) / (degree(v) * (degree(v) - 1))

        Here, `num_edges` represents the number of edges between the
        neighbors of node `v`, and `degree(v)` represents the degree of the
        node, i.e., the number of edges connected to the node.

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n1, dst=n3),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n4, dst=n5),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n3, dst=n5),
        ... )
        >>>
        >>> # 3. Select the local clustering coefficient for each node
        >>> node, coeff = Node.ref("node"), Float.ref("coeff")
        >>> lcc = graph.local_clustering_coefficient()
        >>> select(node.id, coeff).where(lcc(node, coeff)).inspect()
        ▰▰▰▰ Setup complete
           id     coeff
        0   1  1.000000
        1   2  0.666667
        2   3  0.666667
        3   4  0.333333
        4   5  0.000000


        See Also
        --------
        average_clustering_coefficient

        """
        if self.directed:
            # TODO: Eventually make this error more similar to
            #   the corresponding error emitted from the pyrel graphlib wrapper.
            raise NotImplementedError(
                "`local_clustering_coefficient` is not applicable to directed graphs"
            )
        return self._local_clustering_coefficient

    @cached_property
    def _local_clustering_coefficient(self):
        """
        Lazily define and cache the self._local_clustering_coefficient relationship,
        which only applies to undirected graphs.
        """
        _local_clustering_coefficient_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has local clustering coefficient {{coefficient:Float}}")

        if self.directed:
            raise NotImplementedError(
                "`local_clustering_coefficient is not defined for directed graphs."
            )

        node = self.Node.ref()
        degree_no_self = Integer.ref()
        triangle_count = Integer.ref()
        where(
            node,
            _lcc := where(
                self._degree_no_self(node, degree_no_self),
                self._triangle_count(node, triangle_count),
                degree_no_self > 1
            ).select(
                2.0 * triangle_count / (degree_no_self * (degree_no_self - 1.0))
            ) | 0.0,
        ).define(_local_clustering_coefficient_rel(node, _lcc))

        return _local_clustering_coefficient_rel

    @cached_property
    def _degree_no_self(self):
        """
        Lazily define and cache the self._degree_no_self relationship,
        a non-public helper for local_clustering_coefficient.
        """
        _degree_no_self_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} has degree excluding self loops {{num:Integer}}")

        node, neighbor = self.Node.ref(), self.Node.ref()
        where(
            self.Node(node),
            _dns := count(neighbor).per(node).where(self._no_loop_edge(node, neighbor)) | 0,
        ).define(_degree_no_self_rel(node, _dns))

        return _degree_no_self_rel


    @include_in_docs
    def average_clustering_coefficient(self):
        """Returns a unary relationship containing the average clustering coefficient of the graph.

        The average clustering coefficient is the average of the local
        clustering coefficients of the nodes in a graph.

        Returns
        -------
        Relationship
            A unary relationship containing the average clustering coefficient
            of the graph.

        Raises
        ------
        NotImplementedError
            If the graph is directed.

        Relationship Schema
        -------------------
        ``average_clustering_coefficient(coefficient)``

        * **coefficient** (*Float*): The average clustering coefficient of the graph.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes              |
        | :--------- | :-------- | :----------------- |
        | Undirected | Yes       |                    |
        | Directed   | No        | Undirected only.   |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n1, dst=n3),
        ...     Edge.new(src=n1, dst=n4),
        ...     Edge.new(src=n1, dst=n5),
        ...     Edge.new(src=n2, dst=n3),
        ... )
        >>>
        >>> # 3. Inspect the average clustering coefficient
        >>> graph.average_clustering_coefficient().inspect()
        ▰▰▰▰ Setup complete
              float
        0  0.433333

        See Also
        --------
        local_clustering_coefficient

        """
        if self.directed:
            raise NotImplementedError(
                "`average_clustering_coefficient` is not applicable to directed graphs"
            )
        return self._average_clustering_coefficient

    @cached_property
    def _average_clustering_coefficient(self):
        """
        Lazily define and cache the self._average_clustering_coefficient relationship,
        which only applies to undirected graphs.
        """
        _average_clustering_coefficient_rel = self._model.Relationship("The graph has average clustering coefficient {{coefficient:Float}}")

        if self.directed:
            raise NotImplementedError(
                "`average_clustering_coefficient` is not defined for directed graphs."
            )

        node = self.Node.ref()
        coefficient = Float.ref()
        where(
            _avg_coefficient := avg(node, coefficient).where(
                    self._local_clustering_coefficient(node, coefficient)
                ) | 0.0
        ).define(_average_clustering_coefficient_rel(_avg_coefficient))

        return _average_clustering_coefficient_rel


    @include_in_docs
    def reachable_from(self):
        """Returns a binary relationship of all pairs of nodes (u, v) where v is reachable from u.

        A node `v` is considered reachable from a node `u` if there is a path
        of edges from `u` to `v`.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a start node and a
            node that is reachable from it.

        Relationship Schema
        -------------------
        ``reachable_from(start_node, end_node)``

        * **start_node** (*Node*): The node from which the path originates.
        * **end_node** (*Node*): The node that is reachable from the start node.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        There is a slight difference between `transitive closure` and
        `reachable_from`. The transitive closure of a binary relation E is the
        smallest relation that contains E and is transitive. When E is the
        edge set of a graph, the transitive closure of E does not include
        (u, u) if u is isolated. `reachable_from` is a different binary
        relation in which any node u is always reachable from u. In
        particular, `transitive closure` is a more general concept than
        `reachable_from`.

        Examples
        --------
        **Directed Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ... )
        >>>
        >>> # 3. Select all reachable pairs and inspect
        >>> start_node, end_node = Node.ref("start"), Node.ref("end")
        >>> reachable_from = graph.reachable_from()
        >>> select(start_node.id, end_node.id).where(reachable_from(start_node, end_node)).inspect()
        ▰▰▰▰ Setup complete
           id  id2
        0   1    1
        1   1    2
        2   2    2
        3   3    2
        4   3    3


        **Undirected Graph Example**

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define the same nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ... )
        >>>
        >>> # 3. Select all reachable pairs and inspect
        >>> start_node, end_node = Node.ref("start"), Node.ref("end")
        >>> reachable_from = graph.reachable_from()
        >>> select(start_node.id, end_node.id).where(reachable_from(start_node, end_node)).inspect()
        ▰▰▰▰ Setup complete
           id  id2
        0   1    1
        1   1    2
        2   1    3
        3   2    1
        4   2    2
        5   2    3
        6   3    1
        7   3    2
        8   3    3


        """
        warnings.warn(
            (
                "`reachable_from` presently always computes the full transitive closure "
                "of the graph. To provide better control over the computed subset, "
                "`reachable_from`'s interface will soon need to change."
            ),
            FutureWarning,
            stacklevel=2
        )
        return self._reachable_from

    @cached_property
    def _reachable_from(self):
        """Lazily define and cache the self._reachable_from relationship."""
        _reachable_from_rel = self._model.Relationship(f"{{node_a:{self._NodeConceptStr}}} reaches {{node_b:{self._NodeConceptStr}}}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        define(_reachable_from_rel(node_a, node_a))
        define(_reachable_from_rel(node_a, node_c)).where(_reachable_from_rel(node_a, node_b), self._edge(node_b, node_c))

        return _reachable_from_rel


    @include_in_docs
    def distance(self):
        """Returns a ternary relationship containing the shortest path length between all pairs of nodes.

        This method computes the shortest path length between all pairs of
        reachable nodes. The calculation depends on whether the graph is
        weighted:

        * For **unweighted** graphs, the length is the number of edges in the
            shortest path.
        * For **weighted** graphs, the length is the sum of edge weights
            along the shortest path. Edge weights are assumed to be non-negative.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and the shortest path length between them.

        Relationship Schema
        -------------------
        ``distance(start_node, end_node, length)``

        * **start_node** (*Node*): The start node of the path.
        * **end_node** (*Node*): The end node of the path.
        * **length** (*Integer* or *Float*): The shortest path length, returned
        as an Integer for unweighted graphs and a Float for weighted graphs.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                      |
        | :--------- | :-------- | :----------------------------------------- |
        | Undirected | Yes       |                                            |
        | Directed   | Yes       |                                            |
        | Weighted   | Yes       | The calculation uses edge weights.         |

        Examples
        --------
        **Unweighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an unweighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ... )
        >>>
        >>> # 3. Select the shortest path length between all pairs of nodes
        >>> start, end = Node.ref("start"), Node.ref("end")
        >>> length = Integer.ref("length")
        >>> distance = graph.distance()
        >>> select(start.id, end.id, length).where(distance(start, end, length)).inspect()
        ▰▰▰▰ Setup complete
            id  id2  length
        0    1    1       0
        1    1    2       1
        2    1    3       2
        3    1    4       2
        4    2    1       1
        5    2    2       0
        6    2    3       1
        7    2    4       1
        8    3    1       2
        9    3    2       1
        10   3    3       0
        11   3    4       2
        12   4    1       2
        13   4    2       1
        14   4    3       2
        15   4    4       0


        **Weighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a weighted, directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=2.0),
        ...     Edge.new(src=n1, dst=n3, weight=0.5),
        ...     Edge.new(src=n2, dst=n1, weight=1.5),
        ... )
        >>>
        >>> # 3. Select the shortest path length between all pairs of nodes
        >>> start, end = Node.ref("start"), Node.ref("end")
        >>> length = Float.ref("length")
        >>> distance = graph.distance()
        >>> select(start.id, end.id, length).where(distance(start, end, length)).inspect()
        ▰▰▰▰ Setup complete
           id  id2  length
        0   1    1     0.0
        1   1    2     2.0
        2   1    3     0.5
        3   2    1     1.5
        4   2    2     0.0
        5   2    3     2.0
        6   3    3     0.0

        """
        warnings.warn(
            (
                "`distance` presently always computes all-to-all distances "
                "of the graph. To provide better control over the computed subset, "
                "`distance`'s interface will soon need to change."
            ),
            FutureWarning,
            stacklevel=2
        )

        return self._distance

    @cached_property
    def _distance(self):
        """Lazily define and cache the self._distance relationship."""
        if not self.weighted:
            return self._distance_non_weighted
        else:
            return self._distance_weighted

    @cached_property
    def _distance_weighted(self):
        """Lazily define and cache the self._distance_weighted relationship, a non-public helper."""
        _distance_weighted_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have a distance of {{d:Float}}")
        node_u, node_v, node_n, w, d1 = self.Node.ref(), self.Node.ref(),\
            self.Node.ref(), Float.ref(), Float.ref()
        node_u, node_v, d = union(
            where(node_u == node_v, d1 == 0.0).select(node_u, node_v, d1), # Base case.
            where(self._weight(node_n, node_v, w), d2 := _distance_weighted_rel(node_u, node_n, Float) + abs(w))\
            .select(node_u, node_v, d2) # Recursive case.
        )
        define(_distance_weighted_rel(node_u, node_v, min(d).per(node_u, node_v)))

        return _distance_weighted_rel

    @cached_property
    def _distance_non_weighted(self):
        """Lazily define and cache the self._distance_non_weighted relationship, a non-public helper."""
        _distance_non_weighted_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have a distance of {{d:Integer}}")
        node_u, node_v, node_n, d1 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Integer.ref()
        node_u, node_v, d = union(
            where(node_u == node_v, d1 == 0).select(node_u, node_v, d1), # Base case.
            where(self._edge(node_n, node_v),
                  d2 := _distance_non_weighted_rel(node_u, node_n, Integer) + 1).select(node_u, node_v, d2) # Recursive case.
        )
        define(_distance_non_weighted_rel(node_u, node_v, min(d).per(node_u, node_v)))

        return _distance_non_weighted_rel

    @cached_property
    def _distance_reversed_non_weighted(self):
        """Lazily define and cache the self._distance_reversed_non_weighted relationship, a non-public helper."""
        _distance_reversed_non_weighted_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have a reversed distance of {{d:Integer}}")
        node_u, node_v, node_n, d1 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Integer.ref()
        node_u, node_v, d = union(
            where(node_u == node_v, d1 == 0).select(node_u, node_v, d1), # Base case.
            where(self._edge(node_v, node_n),
                  d2 := _distance_reversed_non_weighted_rel(node_u, node_n, Integer) + 1).select(node_u, node_v, d2) # Recursive case.
        )
        define(_distance_reversed_non_weighted_rel(node_u, node_v, min(d).per(node_u, node_v)))

        return _distance_reversed_non_weighted_rel


    @include_in_docs
    def weakly_connected_component(self):
        """Returns a binary relationship that maps each node to its weakly connected component.

        A weakly connected component is a subgraph where for every pair of
        nodes, there is a path between them in the underlying undirected graph.
        For undirected graphs, this is equivalent to finding the connected
        components.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and the
            identifier of the component it belongs to.

        Relationship Schema
        -------------------
        ``weakly_connected_component(node, component_id)``

        * **node** (*Node*): The node.
        * **component_id** (*Node*): The identifier for the component.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        The ``component_id`` is the node with the minimum ID within each
        component.

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a directed graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3 = [Node.new(id=i) for i in range(1, 4)]
        >>> define(n1, n2, n3)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ... )
        >>>
        >>> # 3. Select the component ID for each node and inspect
        >>> node, component_id = Node.ref("node"), Node.ref("component_id")
        >>> wcc = graph.weakly_connected_component()
        >>> select(node.id, component_id.id).where(wcc(node, component_id)).inspect()
        ▰▰▰▰ Setup complete
           id  id2
        0   1    1
        1   2    1
        2   3    1

        """
        warnings.warn(
            (
                "`weakly_connected_component` presently always computes the component "
                "for every node of the graph. To provide better control over the computed subset, "
                "`weakly_connected_component`'s interface will soon need to change."
            ),
            FutureWarning,
            stacklevel=2
        )

        return self._weakly_connected_component

    @cached_property
    def _weakly_connected_component(self):
        """Lazily define and cache the self._weakly_connected_component relationship."""
        _weakly_connected_component_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} is in the connected component {{id:{self._NodeConceptStr}}}")

        node, node_v, component = self.Node.ref(), self.Node.ref(), self.Node.ref()
        node, component = union(
            # A node starts with itself as the component id.
            where(node == component).select(node, component),
            # Recursive case.
            where(_weakly_connected_component_rel(node, component), self._neighbor(node, node_v)).select(node_v, component)
        )
        define(_weakly_connected_component_rel(node, min(component).per(node)))

        return _weakly_connected_component_rel


    @include_in_docs
    def diameter_range(self):
        """Estimates the graph diameter and returns it as a minimum and maximum bound.

        Returns
        -------
        (Relationship, Relationship)
            A tuple containing two unary `Relationship` objects:
            (`min_bound`, `max_bound`).

            * ``min_bound``: A relationship of the form ``min_bound(value)``
                where ``value`` (*Integer*) is the lower bound of the
                estimated diameter.
            * ``max_bound``: A relationship of the form ``max_bound(value)``
                where ``value`` (*Integer*) is the upper bound of the
                estimated diameter.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        This method is used to determine the range of possible diameter
        values in the graph. This is done by selecting a number of random
        nodes in the graph and taking the maximum of all shortest paths
        lengths to the rest of the graph. This gives a range per node.
        Then, the intersection of these ranges is taken and the final range
        is returned.

        For disconnected graphs, `diameter_range` returns the diameter range
        of the largest (weakly) connected component. This behavior deviates
        from many graph theory resources, which typically define the diameter
        of a disconnected graph as infinity.

        Examples
        --------
        **Connected Graph Example**

        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a connected, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>>
        >>> # 3. Get the diameter range and inspect each bound
        >>> min_bound, max_bound = graph.diameter_range()
        >>> min_bound.inspect()
        ▰▰▰▰ Setup complete
           int
        0    3
        >>> max_bound.inspect()
           int
        0    4

        **Disconnected Graph Example**

        >>> from relationalai.semantics import Model, define
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a disconnected, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n4),
        ...     Edge.new(src=n4, dst=n5),
        ... )
        >>>
        >>> # 3. The range reflects the largest component {3, 4, 5}
        >>> min_bound, max_bound = graph.diameter_range()
        >>> min_bound.inspect()
        ▰▰▰▰ Setup complete
           int
        0    2
        >>> max_bound.inspect()
           int
        0    2

        """
        return self._diameter_range

    @cached_property
    def _diameter_range(self):
        """
        Lazily define and cache self._diameter_range, a two-tuple of relationships
        of the form `(_diameter_range_min_rel, _diameter_range_max_rel)`.
        """
        _diameter_range_min_rel = self._model.Relationship("The graph has a min diameter range of {value:Integer}")
        _diameter_range_max_rel = self._model.Relationship("The graph has a max diameter range of {value:Integer}")

        component_node_pairs = self._model.Relationship(f"component id {{cid:{self._NodeConceptStr}}} has node id {{nid:{self._NodeConceptStr}}}")
        nodeid, cid, degreevalue = self.Node.ref(), self.Node.ref(), Integer.ref()
        where(self._degree(nodeid, degreevalue),
              self._weakly_connected_component(nodeid, cid),
              # This is `bottom[10, ...]` in Rel.
              r := (rank(desc(degreevalue, nodeid))), r <= 10)\
              .define(component_node_pairs(cid, nodeid))

        component_node_length = self._model.Relationship(f"component id {{cid:{self._NodeConceptStr}}} and node id {{nid:{self._NodeConceptStr}}} have max distance {{mdist:Integer}}")

        cid, nid = self.Node.ref(), self.Node.ref()

        if self.directed:
            where(component_node_pairs(cid, nid),
                  # Weights are ignored!
                  max_forward := max(self._distance_non_weighted(nid, self.Node.ref(), Integer.ref())).per(nid),
                  max_reversed := max(self._distance_reversed_non_weighted(nid, self.Node.ref(), Integer.ref())).per(nid),
                  max_sp := maximum(max_forward, max_reversed))\
                .define(component_node_length(cid, nid, max_sp))
        else:
            where(component_node_pairs(cid, nid),
                  # Weights are ignored!
                  max_sp := max(self._distance_non_weighted(nid, self.Node, Integer)).per(nid))\
                .define(component_node_length(cid, nid, max_sp))

        component_of_interest = self._model.Relationship(f"component id {{cid:{self._NodeConceptStr}}} is of interest")

        v = Integer.ref()
        where(v == max(component_node_length(self.Node.ref(), self.Node.ref(), Integer)),
              component_node_length(cid, self.Node.ref(), v)
              ).define(component_of_interest(cid))

        candidates = self._model.Relationship(f"node with id {{nodeid:{self._NodeConceptStr}}} and length {{value:Integer}} are candidates")
        nodeid, value = self.Node.ref(), Integer.ref()
        where(component_node_length(cid, nodeid, value),
              component_of_interest(cid))\
              .define(candidates(nodeid, value))

        where(v := min(candidates(nodeid, Integer))).define(_diameter_range_max_rel(2 * v))
        where(v := max(candidates(nodeid, Integer))).define(_diameter_range_min_rel(v))

        return (_diameter_range_min_rel, _diameter_range_max_rel)

    @cached_property
    def _reachable_from_min_node(self):
        """Lazily define and cache the self._reachable_from_min_node relationship, a non-public helper."""
        _reachable_from_min_node_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} is reachable from the minimal node")

        node_v, node_w = self.Node.ref(), self.Node.ref()
        define(_reachable_from_min_node_rel(min(node_v)))
        where(_reachable_from_min_node_rel(node_w), self._edge(node_w, node_v)).define(_reachable_from_min_node_rel(node_v))
        # We discard directions for `is_connected`.
        where(_reachable_from_min_node_rel(node_w), self._edge(node_v, node_w)).define(_reachable_from_min_node_rel(node_v))

        return _reachable_from_min_node_rel


    @include_in_docs
    def is_connected(self):
        """Returns a query fragment that is satisfied if the graph is connected.

        A graph is considered connected if every node is reachable from every
        other node in the underlying undirected graph.

        Returns
        -------
        Fragment
            A query fragment that can be used as a condition in other
            queries to assert that the graph is connected.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        An empty graph is considered connected.

        Examples
        --------
        **Connected Graph Example**

        The following query will produce a result because the graph is connected.

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a connected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>>
        >>> # 3. Use the fragment as a condition in a query
        >>> select("Graph is connected").where(graph.is_connected()).inspect()
        ▰▰▰▰ Setup complete
                            v
        0  Graph is connected

        **Disconnected Graph Example**

        The following query will produce no results because the graph is not
        connected.

        >>> from relationalai.semantics import Model, define, select
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a disconnected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5 = [Node.new(id=i) for i in range(1, 6)]
        >>> define(n1, n2, n3, n4, n5)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n3, dst=n2),
        ...     Edge.new(src=n4, dst=n5),  # This edge creates a separate component
        ... )
        >>>
        >>> # 3. The conditional query produces no output
        >>> select("Graph is connected").where(graph.is_connected()).inspect()
        ▰▰▰▰ Setup complete
        Empty DataFrame
        Columns: []
        Index: []

        """
        # TODO (dba) This method is inconsistent with the other,
        # public methods. It does not return a `Relationship`. Revisit
        # this. See GH thread:
        # https://github.com/RelationalAI/relationalai-python/pull/2077#discussion_r2190538074
        return where(
            self._num_nodes(0) |
            count(self._reachable_from_min_node(self.Node.ref())) == self._num_nodes(Integer.ref())
        )


    @include_in_docs
    def jaccard_similarity(self):
        """Returns a ternary relationship containing the Jaccard similarity for all pairs of nodes.

        The Jaccard similarity is a measure between two nodes that ranges from
        0.0 to 1.0, where higher values indicate greater similarity.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their Jaccard similarity.

        Relationship Schema
        -------------------
        ``jaccard_similarity(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Float*): The Jaccard similarity of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                      |
        | :--------- | :-------- | :----------------------------------------- |
        | Undirected | Yes       |                                            |
        | Directed   | Yes       | Based on out-neighbors.                    |
        | Weighted   | Yes       |                                            |
        | Unweighted | Yes       | Each edge weight is taken to be 1.0.       |

        Notes
        -----
        The **unweighted** Jaccard similarity between two nodes is the ratio of
        the size of the intersection to the size of the union of their
        neighbors (or out-neighbors for directed graphs).

        The **weighted** Jaccard similarity considers the weights of the edges.
        The definition used here is taken from the reference noted below. It is
        the ratio between two quantities:

        1.  **Numerator**: For every other node `w` in the graph, find the
            minimum of the edge weights `(u, w)` and `(v, w)`, and sum these
            minimums.
        2.  **Denominator**: For every other node `w` in the graph, find the
            maximum of the edge weights `(u, w)` and `(v, w)`, and sum these
            maximums.

        If an edge does not exist, its weight is considered 0.0. This can be
        better understood via the following calculation for the weighted
        example below.

        | node id | edge weights to node 1 | edge weights to node 2 | min  | max  |
        | :------ | :--------------------- | :--------------------- | :--- | :--- |
        | 1       | 0.0                    | 1.6                    | 0.0  | 1.6  |
        | 2       | 1.6                    | 0.0                    | 0.0  | 1.6  |
        | 3       | 1.4                    | 0.46                   | 0.46 | 1.4  |
        | 4       | 0.0                    | 0.0                    | 0.0  | 0.0  |

        The weighted Jaccard similarity between node 1 and 2 is then:
        `0.46 / (1.6 + 1.6 + 1.4) = 0.1`.

        Examples
        --------
        **Unweighted Graph Examples**

        *Undirected Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 2, v.id == 4).inspect()
        ▰▰▰▰ Setup complete
           score
        0   0.25

        *Directed Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 2, v.id == 4).inspect()
        ▰▰▰▰ Setup complete
           score
        0    0.5

        **Weighted Graph Example**

        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up a weighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges with weights
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.6),
        ...     Edge.new(src=n1, dst=n3, weight=1.4),
        ...     Edge.new(src=n2, dst=n3, weight=0.46),
        ...     Edge.new(src=n3, dst=n4, weight=2.5),
        ... )
        >>>
        >>> # 3. Select the weighted Jaccard similarity for the pair (1, 2)
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> jaccard = graph.jaccard_similarity()
        >>> select(score).where(jaccard(u, v, score), u.id == 1, v.id == 2).inspect()
        ▰▰▰▰ Setup complete
           score
        0    0.1

        References
        ----------
        Frigo M, Cruciani E, Coudert D, Deriche R, Natale E, Deslauriers-Gauthier S.
        Network alignment and similarity reveal atlas-based topological differences
        in structural connectomes. Netw Neurosci. 2021 Aug 30;5(3):711-733.
        doi: 10.1162/netn_a_00199. PMID: 34746624; PMCID: PMC8567827.

        """
        warnings.warn(
            (
                "`jaccard_similarity` presently always computes the similarity "
                "of all pairs of nodes of the graph. To provide better control over "
                "the computed subset, `jaccard_similarity`'s interface will soon "
                "need to change."
            ),
            FutureWarning,
            stacklevel=2
        )
        return self._jaccard_similarity

    @cached_property
    def _jaccard_similarity(self):
        """Lazily define and cache the self._jaccard_similarity relationship."""
        _jaccard_similarity_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} has a similarity to {{node_v:{self._NodeConceptStr}}} of {{similarity:Float}}")

        if not self.weighted:
            node_u, node_v = self.Node.ref(), self.Node.ref()
            num_union_outneighbors, num_u_outneigbor, num_v_outneigbor, f = Integer.ref(),\
                Integer.ref(), Integer.ref(), Float.ref()

            where(num_common_outneighbor := self._count_common_outneighbor_fragment(node_u, node_v),
                  self._count_outneighbor(node_u, num_u_outneigbor),
                  self._count_outneighbor(node_v, num_v_outneigbor),
                  num_union_outneighbors := num_u_outneigbor + num_v_outneigbor - num_common_outneighbor,
                  f := num_common_outneighbor / num_union_outneighbors).define(_jaccard_similarity_rel(node_u, node_v, f))
        else:
            # TODO (dba) Annotate local relationships in this scope with `@ondemand` once available.

            # (1) The numerator: For every node `k` in the graph, find the minimum weight of
            #     the out-edges from `u` and `v` to `k`, and sum those minimum weights.

            #     Note that for any node `k` that is not a common out-neighbor of nodes `u` and `v`,
            #     the minimum weight of the out-edges from `u` and `v` to `k` is zero/empty,
            #     so the sum here reduces to a sum over the common out-neighbors of `u` and `v`.
            min_weight_to_common_outneighbor = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have common outneighbor {{node_k:{self._NodeConceptStr}}} with minimum weight {{minweight:Float}}")

            node_u, node_v, node_k, w1, w2 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Float.ref(), Float.ref()
            w = union(where(self._weight(node_u, node_k, w1)).select(w1),
                      where(self._weight(node_v, node_k, w2)).select(w2))
            where(self._edge(node_u, node_k),
                  self._edge(node_v, node_k))\
                  .define(min_weight_to_common_outneighbor(node_u, node_v, node_k, min(w).per(node_u, node_v, node_k)))

            sum_of_min_weights_to_common_outneighbors = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have a sum of minweights of {{minsum:Float}}")

            minweight = Float.ref()
            where(min_weight_to_common_outneighbor(node_u, node_v, node_k, minweight)
                  ).define(sum_of_min_weights_to_common_outneighbors(node_u, node_v, sum(node_k, minweight).per(node_u, node_v)))

            # (2) The denominator: For every node `k` in the graph, find the maximum weight of
            #     the out-edges from `u` and `v` to `k`, and sum those maximum weights.
            #
            #     Note that in general the sum of the maximum of two quantities,
            #     say \sum_i max(a_i, b_i), can be reexpressed via the following identity
            #     \sum_i max(a_i, b_i) = \sum_i a_i + \sum_i b_i - \sum_i min(a_i, b_i).
            #     This identity allows us to reexpress the sum here:
            #
            #     \sum_{k in self.Node} max(self._weight(u, k), self._weight(v, k)) =
            #         \sum_{k in self.Node} self._weight(u, k) +
            #         \sum_{k in self.Node} self._weight(v, k) -
            #         \sum_{k in self.Node} min(self._weight(u, k), self._weight(v, k))
            #
            #     To simplify this expression, note that `self._weight(u, k)` is zero/empty
            #     for all `k` that aren't out-neighbors of `u`. It follows that
            #
            #     \sum_{k in self.Node} self._weight(u, k)
            #         = \sum_{k in self._outneighbor(u)} self._weight(u, k)
            #         = self._weighted_outdegree(u)
            #
            #     and similarly
            #
            #     \sum_{k in self.Node} self._weight(v, k) = self._weighted_outdegree(v)
            #
            #     Additionally, observe that `min(self._weight(u, k), self._weight(v, k))` is zero/empty
            #     for all `k` that aren't out-neighbors of both `u` and `v`. It follows that
            #
            #     \sum_{k in self.Node} min(self._weight(u, k), self._weight(v, k))
            #         = \sum_{k in self._common_outneighbor(u, v)} min(self._weight(u, k), self._weight(v, k))
            #
            #     which is _sum_of_min_weights_to_common_outneighbors above, which we
            #     can reuse to avoid computation. Finally:
            #
            #     \sum_{k in self.Node} max(self._weight(u, k), self._weight(v, k)) =
            #         self._weighted_outdegree(u) +
            #         self._weighted_outdegree(v) -
            #         _sum_of_min_weights_to_common_outneighbors(u, v)
            sum_of_max_weights_to_other_nodes = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have a maxsum of {{maxsum:Float}}")

            u_outdegree, v_outdegree, maxsum, minsum = Float.ref(), Float.ref(), Float.ref(), Float.ref()
            where(self._weighted_outdegree(node_u, u_outdegree),
                  self._weighted_outdegree(node_v, v_outdegree),
                  sum_of_min_weights_to_common_outneighbors(node_u, node_v, minsum),
                  maxsum == u_outdegree + v_outdegree - minsum
                  ).define(sum_of_max_weights_to_other_nodes(node_u, node_v, maxsum))

            score = Float.ref()
            where(sum_of_min_weights_to_common_outneighbors(node_u, node_v, minsum),
                  sum_of_max_weights_to_other_nodes(node_u, node_v, maxsum),
                  score == minsum/maxsum
                  ).define(_jaccard_similarity_rel(node_u, node_v, score))

        return _jaccard_similarity_rel


    @include_in_docs
    def cosine_similarity(self):
        """Returns a ternary relationship containing the cosine similarity for all pairs of nodes.

        The cosine similarity measures the similarity between two nodes based
        on the angle between their neighborhood vectors. The score ranges from
        0.0 to 1.0, inclusive, where 1.0 indicates identical sets of neighbors.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their cosine similarity.

        Relationship Schema
        -------------------
        ``cosine_similarity(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Float*): The cosine similarity of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                                      |
        | :--------- | :-------- | :----------------------------------------- |
        | Undirected | Yes       |                                            |
        | Directed   | Yes       | Based on out-neighbors.                    |
        | Weighted   | Yes       |                                            |
        | Unweighted | Yes       | Each edge weight is taken to be 1.0.       |

        Notes
        -----
        The cosine similarity is defined as the normalized inner product of
        two vectors representing the neighborhoods of the nodes `u` and `v`.
        For directed graphs, only out-neighbors are considered.

        * For **unweighted** graphs, the vector for a node `u` contains a 1
            for each neighbor and a 0 for each non-neighbor.
        * For **weighted** graphs, the vector for a node `u` contains the
            edge weight for each neighbor and a 0 for each non-neighbor.

        Edge weights are assumed to be non-negative, so the neighborhood
        vectors contain only non-negative elements. Therefore, the cosine
        similarity score is always between 0.0 and 1.0, inclusive.

        Examples
        --------
        **Unweighted Graph Examples**

        *Undirected Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> cosine_similarity = graph.cosine_similarity()
        >>> select(score).where(cosine_similarity(u, v, score), u.id == 2, v.id == 4).inspect()
        ▰▰▰▰ Setup complete
              score
        0  0.408248

        *Directed Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> cosine_similarity = graph.cosine_similarity()
        >>> select(score).where(cosine_similarity(u, v, score), u.id == 2, v.id == 4).inspect()
        ▰▰▰▰ Setup complete
              score
        0  0.707107

        **Weighted Graph Examples**

        *Undirected Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4, n13, n14 = [Node.new(id=i) for i in [1, 2, 3, 4, 13, 14]]
        >>> define(n1, n2, n3, n4, n13, n14)
        >>> define(
        ...     Edge.new(src=n1, dst=n2, weight=1.6),
        ...     Edge.new(src=n1, dst=n3, weight=1.4),
        ...     Edge.new(src=n2, dst=n3, weight=1.2),
        ...     Edge.new(src=n3, dst=n4, weight=2.5),
        ...     Edge.new(src=n14, dst=n13, weight=1.0),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> cosine_similarity = graph.cosine_similarity()
        >>> select(score).where(cosine_similarity(u, v, score), u.id == 1, v.id == 2).inspect()
        ▰▰▰▰ Setup complete
              score
        0  0.395103

        *Directed Graph*
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=True, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in [1, 2, 3, 4]]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n3, weight=2.0),
        ...     Edge.new(src=n1, dst=n4, weight=3.0),
        ...     Edge.new(src=n2, dst=n3, weight=4.0),
        ...     Edge.new(src=n2, dst=n4, weight=5.0),
        ... )
        >>> u, v, score = Node.ref("u"), Node.ref("v"), Float.ref("score")
        >>> cosine_similarity = graph.cosine_similarity()
        >>> select(score).where(cosine_similarity(u, v, score), u.id == 1, v.id == 2).inspect()
        ▰▰▰▰ Setup complete
              score
        0  0.996241

        """
        warnings.warn(
            (
                "`cosine_similarity` presently always computes the similarity "
                "of all pairs of nodes of the graph. To provide better control over "
                "the computed subset, `cosine_similarity`'s interface will soon "
                "need to change."
            ),
            FutureWarning,
            stacklevel=2
        )

        return self._cosine_similarity

    @cached_property
    def _cosine_similarity(self):
        """Lazily define and cache the self._cosine_similarity relationship."""
        _cosine_similarity_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} has a cosine similarity to {{node_v:{self._NodeConceptStr}}} of {{score:Float}}")

        if not self.weighted:
            node_u, node_v = self.Node.ref(), self.Node.ref()
            count_outneighor_u, count_outneighor_v, score = Integer.ref(), Integer.ref(), Float.ref()

            where(
                self._count_outneighbor(node_u, count_outneighor_u),
                self._count_outneighbor(node_v, count_outneighor_v),
                c_common := self._count_common_outneighbor_fragment(node_u, node_v),
                score := c_common / sqrt(count_outneighor_u * count_outneighor_v),
            ).define(
                _cosine_similarity_rel(node_u, node_v, score)
            )
        else:
            node_u, node_v = self.Node.ref(), self.Node.ref()
            node_uk, node_vk = self.Node.ref(), self.Node.ref()
            wu, wv = Float.ref(), Float.ref()
            where(
                squared_norm_wu := sum(node_uk, wu * wu).per(node_u).where(self._weight(node_u, node_uk, wu)),
                squared_norm_wv := sum(node_vk, wv * wv).per(node_v).where(self._weight(node_v, node_vk, wv)),
                wu_dot_wv := self._wu_dot_wv_fragment(node_u, node_v),
                score := wu_dot_wv / sqrt(squared_norm_wu * squared_norm_wv),
            ).define(
                _cosine_similarity_rel(node_u, node_v, score)
            )

        return _cosine_similarity_rel


    @include_in_docs
    def adamic_adar(self):
        """Returns a ternary relationship containing the Adamic-Adar index for all pairs of nodes.

        The Adamic-Adar index is a similarity measure between two nodes based
        on the amount of shared neighbors between them, giving more weight to
        common neighbors that are less connected.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their Adamic-Adar index.

        Relationship Schema
        -------------------
        ``adamic_adar(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Float*): The Adamic-Adar index of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Notes
        -----
        The Adamic-Adar index for nodes `u` and `v` is defined as the sum of
        the inverse logarithmic degree of their common neighbors `w`::

            AA(u,v) = Σ (1 / log(degree(w)))

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Float
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>>
        >>> # 3. Select the Adamic-Adar index for the pair (2, 4)
        >>> u, v = Node.ref("u"), Node.ref("v")
        >>> score = Float.ref("score")
        >>> adamic_adar = graph.adamic_adar()
        >>> select(
        ...     u.id, v.id, score,
        ... ).where(
        ...     adamic_adar(u, v, score),
        ...     u.id == 2,
        ...     v.id == 4,
        ... ).inspect()
        ▰▰▰▰ Setup complete
           id  id2     score
        0   2    4  0.910239

        """
        warnings.warn(
            (
                "`adamic_adar` presently always computes the similarity "
                "of all pairs of nodes of the graph. To provide better control over "
                "the computed subset, `adamic_adar`'s interface will soon "
                "need to change."
            ),
            FutureWarning,
            stacklevel=2
        )

        return self._adamic_adar

    @cached_property
    def _adamic_adar(self):
        """Lazily define and cache the self._adamic_adar relationship."""
        _adamic_adar_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have adamic adar score {{score:Float}}")

        node_u, node_v, common_neighbor = self.Node.ref(), self.Node.ref(), self.Node.ref()
        neighbor_count = Integer.ref()

        where(
            _score := sum(common_neighbor, 1.0 / natural_log(neighbor_count)).per(node_u, node_v).where(
                self._common_neighbor(node_u, node_v, common_neighbor),
                self._count_neighbor(common_neighbor, neighbor_count),
            )
        ).define(_adamic_adar_rel(node_u, node_v, _score))

        return _adamic_adar_rel


    @include_in_docs
    def preferential_attachment(self):
        """Returns a ternary relationship containing the preferential attachment score for all pairs of nodes.

        The preferential attachment score between two nodes `u` and `v` is the
        number of nodes adjacent to `u` multiplied by the number of nodes
        adjacent to `v`.

        Returns
        -------
        Relationship
            A ternary relationship where each tuple represents a pair of nodes
            and their preferential attachment score.

        Relationship Schema
        -------------------
        ``preferential_attachment(node_u, node_v, score)``

        * **node_u** (*Node*): The first node in the pair.
        * **node_v** (*Node*): The second node in the pair.
        * **score** (*Integer*): The preferential attachment score of the pair.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                |
        | :--------- | :-------- | :------------------- |
        | Undirected | Yes       |                      |
        | Directed   | Yes       |                      |
        | Weighted   | Yes       | Weights are ignored. |

        Examples
        --------
        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4 = [Node.new(id=i) for i in range(1, 5)]
        >>> define(n1, n2, n3, n4)
        >>> define(
        ...     Edge.new(src=n1, dst=n2),
        ...     Edge.new(src=n2, dst=n3),
        ...     Edge.new(src=n3, dst=n3),
        ...     Edge.new(src=n2, dst=n4),
        ...     Edge.new(src=n4, dst=n3),
        ... )
        >>>
        >>> # 3. Select the preferential attachment score for the pair (1, 3)
        >>> u, v = Node.ref("u"), Node.ref("v")
        >>> score = Integer.ref("score")
        >>> preferential_attachment = graph.preferential_attachment()
        >>> select(
        ...     u.id, v.id, score,
        ... ).where(
        ...     preferential_attachment(u, v, score),
        ...     u.id == 1,
        ...     v.id == 3,
        ... ).inspect()
        ▰▰▰▰ Setup complete
           id  id2  score
        0   1    3      3

        """
        warnings.warn(
            (
                "`preferential_attachment` presently always computes the similarity "
                "of all pairs of nodes of the graph. To provide better control over "
                "the computed subset, `preferential_attachment`'s interface will soon "
                "need to change."
            ),
            FutureWarning,
            stacklevel=2
        )

        return self._preferential_attachment

    @cached_property
    def _preferential_attachment(self):
        """Lazily define and cache the self._preferential_attachment relationship."""
        _preferential_attachment_rel = self._model.Relationship(f"{{node_u:{self._NodeConceptStr}}} and {{node_v:{self._NodeConceptStr}}} have preferential attachment score {{score:Integer}}")

        node_u, node_v = self.Node.ref(), self.Node.ref()
        count_u, count_v = Integer.ref(), Integer.ref()

        # NOTE: We consider isolated nodes separately to maintain
        #   the dense behavior of preferential attachment.

        # Case where node u is isolated, and node v is any node: score 0.
        where(
            self._isolated_node(node_u),
            self.Node(node_v),
        ).define(_preferential_attachment_rel(node_u, node_v, 0))

        # Case where node u is any node, and node v is isolated: score 0.
        where(
            self.Node(node_u),
            self._isolated_node(node_v)
        ).define(_preferential_attachment_rel(node_u, node_v, 0))

        # Case where neither node is isolated: score is count_neighbor[u] * count_neighbor[v].
        where(
            self._count_neighbor(node_u, count_u),
            self._count_neighbor(node_v, count_v)
        ).define(_preferential_attachment_rel(node_u, node_v, count_u * count_v))

        return _preferential_attachment_rel

    @cached_property
    def _isolated_node(self):
        """
        Lazily define and cache the self._isolated_node (helper, non-public) relationship.
        At this time, exclusively a helper for preferential_attachment.
        """
        _isolated_node_rel = self._model.Relationship(f"{{node:{self._NodeConceptStr}}} is isolated")

        neighbor_node = self.Node.ref()
        where(
            self.Node,
            not_(self._neighbor(self.Node, neighbor_node))
        ).define(_isolated_node_rel(self.Node))

        return _isolated_node_rel


    def infomap(
            self,
            max_levels: int = 1,
            max_sweeps: int = 20,
            level_tolerance: float = 0.01,
            sweep_tolerance: float = 0.0001,
            teleportation_rate: float = 0.15,
            visit_rate_tolerance: float = 1e-15,
            randomization_seed: int = 8675309,
    ):
        """Partitions nodes into communities using a variant of the Infomap algorithm.

        This method maps nodes to community assignments based on the flow of
        information on the graph.

        Parameters
        ----------
        max_levels : int, optional
            The maximum number of levels at which to optimize. Must be a
            positive integer. Default is 1.
        max_sweeps : int, optional
            The maximum number of sweeps within each level. Must be a non-negative
            integer. Default is 20.
        level_tolerance : float, optional
            Map equation progress threshold to continue to the next level.
            Must be a non-negative float. Default is 0.01.
        sweep_tolerance : float, optional
            Map equation progress threshold to continue to the next sweep.
            Must be a non-negative float. Default is 0.0001.
        teleportation_rate : float, optional
            Teleportation rate for ergodic node visit rate calculation. Must be
            a float in (0, 1]. Default is 0.15.
        visit_rate_tolerance : float, optional
            Convergence tolerance for ergodic node visit rate calculation. Must
            be a positive float. Default is 1e-15.
        randomization_seed : int, optional
            The random number generator seed for the run. Must be a non-negative
            integer. Default is 8675309.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            community assignment.

        Relationship Schema
        -------------------
        ``infomap(node, community_label)``

        * **node** (*Node*): The node.
        * **community_label** (*Integer*): The label of the community the node
        belongs to.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                           |
        | :--------- | :-------- | :------------------------------ |
        | Undirected | Yes       |                                 |
        | Directed   | Yes       |                                 |
        | Weighted   | Yes       | Only positive weights supported.|
        | Unweighted | Yes       |                                 |

        Notes
        -----
        This implementation of Infomap minimizes the map equation via a
        Louvain-like optimization heuristic; this is often referred to as
        "core" Infomap in the literature. Computation of the ergodic node
        visit frequencies is done via regularized power iteration, with
        regularization via a uniform teleportation probability of 0.15,
        matching the nominal selection in the literature.

        Examples
        --------
        **Unweighted Graph Example**

        Compute community assignments for each node in an undirected graph. Here,
        an undirected dumbbell graph resolves into two communities, namely its
        two constituent three-cliques.

        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges for a dumbbell graph
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # The first three-clique.
        ...     Edge.new(src=n1, dst=n2), Edge.new(src=n1, dst=n3), Edge.new(src=n2, dst=n3),
        ...     # The second three-clique.
        ...     Edge.new(src=n4, dst=n5), Edge.new(src=n4, dst=n6), Edge.new(src=n5, dst=n6),
        ...     # The connection between the three-cliques.
        ...     Edge.new(src=n1, dst=n4)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> infomap = graph.infomap()
        >>> select(node.id, label).where(infomap(node, label)).inspect()
        # The output will show each node mapped to a community:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        **Weighted Graph Example**

        Compute community assignments for each node in an undirected weighted
        graph. Here, a six-clique has the edges forming a dumbbell graph
        within the six-clique strongly weighted, and the remaining edges
        weakly weighted. The graph resolves into two communities, namely the
        two three-cliques constituent of the dumbbell embedded in the six-clique.

        >>> # 1. Set up a weighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # First embedded three-clique.
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n1, dst=n3, weight=1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ...     # Second embedded three-clique.
        ...     Edge.new(src=n4, dst=n5, weight=1.0),
        ...     Edge.new(src=n4, dst=n6, weight=1.0),
        ...     Edge.new(src=n5, dst=n6, weight=1.0),
        ...     # Slightly weaker connection between the embedded three-cliques.
        ...     Edge.new(src=n1, dst=n4, weight=0.5),
        ...     # Weaker edges connecting the six-clique in full.
        ...     Edge.new(src=n1, dst=n5, weight=0.1), Edge.new(src=n1, dst=n6, weight=0.1),
        ...     Edge.new(src=n2, dst=n4, weight=0.1), Edge.new(src=n2, dst=n5, weight=0.1),
        ...     Edge.new(src=n2, dst=n6, weight=0.1), Edge.new(src=n3, dst=n4, weight=0.1),
        ...     Edge.new(src=n3, dst=n5, weight=0.1), Edge.new(src=n3, dst=n6, weight=0.1)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> infomap = graph.infomap()
        >>> select(node.id, label).where(infomap(node, label)).inspect()
        # The output will show the two-community dumbbell structure:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        """
        _assert_type("infomap:max_levels", max_levels, int)
        _assert_type("infomap:max_sweeps", max_sweeps, int)
        _assert_exclusive_lower_bound("infomap:max_levels", max_levels, 0)
        _assert_inclusive_lower_bound("infomap:max_sweeps", max_sweeps, 0)

        _assert_type("infomap:level_tolerance", level_tolerance, Real)
        _assert_type("infomap:sweep_tolerance", sweep_tolerance, Real)
        _assert_inclusive_lower_bound("infomap:level_tolerance", level_tolerance, 0.0)
        _assert_inclusive_lower_bound("infomap:sweep_tolerance", sweep_tolerance, 0.0)

        _assert_type("infomap:teleportation_rate", teleportation_rate, Real)
        _assert_inclusive_lower_bound("infomap:teleportation_rate", teleportation_rate, 1e-4)
        _assert_exclusive_upper_bound("infomap:teleportation_rate", teleportation_rate, 1.0)

        _assert_type("infomap:visit_rate_tolerance", visit_rate_tolerance, Real)
        _assert_exclusive_lower_bound("infomap:visit_rate_tolerance", visit_rate_tolerance, 0.0)

        _assert_type("infomap:randomization_seed", randomization_seed, int)
        _assert_exclusive_lower_bound("infomap:randomization_seed", randomization_seed, 0)

        raise NotImplementedError("`infomap` is not yet implemented.")

    def louvain(
            self,
            max_levels: int = 1,
            max_sweeps: int = 20,
            level_tolerance: float = 0.01,
            sweep_tolerance: float = 0.0001,
            randomization_seed: int = 8675309,
    ):
        """Partitions nodes into communities using the Louvain algorithm.

        This method detects communities by maximizing a modularity score. It is
        only applicable to undirected graphs.

        Parameters
        ----------
        max_levels : int, optional
            The maximum number of levels at which to optimize. Must be a
            positive integer. Default is 1.
        max_sweeps : int, optional
            The maximum number of sweeps within each level. Must be a
            non-negative integer. Default is 20.
        level_tolerance : float, optional
            Modularity progress threshold to continue to the next level.
            Must be a non-negative float. Default is 0.01.
        sweep_tolerance : float, optional
            Modularity progress threshold to continue to the next sweep.
            Must be a non-negative float. Default is 0.0001.
        randomization_seed : int, optional
            The random number generator seed for the run. Must be a
            non-negative integer. Default is 8675309.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            community assignment.

        Raises
        ------
        DirectedGraphNotSupported
            If the graph is directed.

        Relationship Schema
        -------------------
        ``louvain(node, community_label)``

        * **node** (*Node*): The node.
        * **community_label** (*Integer*): The label of the community the node
        belongs to.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                           |
        | :--------- | :-------- | :------------------------------ |
        | Undirected | Yes       |                                 |
        | Directed   | No        | Not supported by this implementation. |
        | Weighted   | Yes       | Only positive weights supported.|
        | Unweighted | Yes       |                                 |

        Notes
        -----
        This implementation of the Louvain algorithm is consistent with the
        modularity definition (Eq. 1) in "Fast unfolding of communities in
        large networks", Blondel et al J. Stat. Mech. (2008) P10008.

        Examples
        --------
        **Unweighted Graph Example**

        Compute community assignments for each node in an undirected graph.
        Here, an undirected dumbbell graph resolves into two communities,
        namely its two constituent three-cliques.

        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges for a dumbbell graph
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # The first three-clique.
        ...     Edge.new(src=n1, dst=n2), Edge.new(src=n1, dst=n3), Edge.new(src=n2, dst=n3),
        ...     # The second three-clique.
        ...     Edge.new(src=n4, dst=n5), Edge.new(src=n4, dst=n6), Edge.new(src=n5, dst=n6),
        ...     # The connection between the three-cliques.
        ...     Edge.new(src=n1, dst=n4)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> louvain = graph.louvain()
        >>> select(node.id, label).where(louvain(node, label)).inspect()
        # The output will show each node mapped to a community:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        **Weighted Graph Example**

        Compute community assignments for each node in an undirected weighted
        graph. Here, a six-clique has the edges forming a dumbbell graph
        within the six-clique strongly weighted, and the remaining edges
        weakly weighted. The graph resolves into two communities, namely the
        two three-cliques constituent of the dumbbell embedded in the
        six-clique.

        >>> # 1. Set up a weighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # First embedded three-clique.
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n1, dst=n3, weight=1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ...     # Second embedded three-clique.
        ...     Edge.new(src=n4, dst=n5, weight=1.0),
        ...     Edge.new(src=n4, dst=n6, weight=1.0),
        ...     Edge.new(src=n5, dst=n6, weight=1.0),
        ...     # Connection between the embedded three-cliques.
        ...     Edge.new(src=n1, dst=n4, weight=1.0),
        ...     # Weaker edges connecting the six-clique in full.
        ...     Edge.new(src=n1, dst=n5, weight=0.2), Edge.new(src=n1, dst=n6, weight=0.2),
        ...     Edge.new(src=n2, dst=n4, weight=0.2), Edge.new(src=n2, dst=n5, weight=0.2),
        ...     Edge.new(src=n2, dst=n6, weight=0.2), Edge.new(src=n3, dst=n4, weight=0.2),
        ...     Edge.new(src=n3, dst=n5, weight=0.2), Edge.new(src=n3, dst=n6, weight=0.2)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> louvain = graph.louvain()
        >>> select(node.id, label).where(louvain(node, label)).inspect()
        # The output will show the two-community dumbbell structure:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        """
        if self.directed:
            raise DirectedGraphNotSupported("louvain")

        _assert_type("louvain:max_levels", max_levels, int)
        _assert_type("louvain:max_sweeps", max_sweeps, int)
        _assert_exclusive_lower_bound("louvain:max_levels", max_levels, 0)
        _assert_inclusive_lower_bound("louvain:max_sweeps", max_sweeps, 0)

        _assert_type("louvain:level_tolerance", level_tolerance, Real)
        _assert_type("louvain:sweep_tolerance", sweep_tolerance, Real)
        _assert_inclusive_lower_bound("louvain:level_tolerance", level_tolerance, 0.0)
        _assert_inclusive_lower_bound("louvain:sweep_tolerance", sweep_tolerance, 0.0)

        _assert_type("louvain:randomization_seed", randomization_seed, int)
        _assert_exclusive_lower_bound("louvain:randomization_seed", randomization_seed, 0)

        raise NotImplementedError("`louvain` is not yet implemented.")

    def label_propagation(
            self,
            max_sweeps: int = 20,
            randomization_seed: int = 8675309,
    ):
        """Partitions nodes into communities using the Label Propagation algorithm.

        This method maps nodes to community assignments via asynchronous
        label propagation.

        Parameters
        ----------
        max_sweeps : int, optional
            The maximum number of sweeps for label propagation to perform.
            Must be a positive integer. Default is 20.
        randomization_seed : int, optional
            The random number generator seed for the run. Must be a positive
            integer. Default is 8675309.

        Returns
        -------
        Relationship
            A binary relationship where each tuple represents a node and its
            community assignment.

        Relationship Schema
        -------------------
        ``label_propagation(node, community_label)``

        * **node** (*Node*): The node.
        * **community_label** (*Integer*): The label of the community the node
        belongs to.

        Supported Graph Types
        ---------------------
        | Graph Type | Supported | Notes                           |
        | :--------- | :-------- | :------------------------------ |
        | Undirected | Yes       |                                 |
        | Directed   | Yes       |                                 |
        | Weighted   | Yes       | Only positive weights supported.|
        | Unweighted | Yes       |                                 |

        Notes
        -----
        This implementation of asynchronous label propagation breaks ties
        between neighboring labels with equal cumulative edge weight (and
        frequency in the unweighted case) uniformly at random, but with a
        static seed.

        Examples
        --------
        **Unweighted Graph Example**

        Compute community assignments for each node in an undirected graph. Here,
        an undirected dumbbell graph resolves into two communities, namely its
        two constituent three-cliques.

        >>> from relationalai.semantics import Model, define, select, Integer
        >>> from relationalai.semantics.reasoners.graph import Graph
        >>>
        >>> # 1. Set up an undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=False)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges for a dumbbell graph
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # The first three-clique.
        ...     Edge.new(src=n1, dst=n2), Edge.new(src=n1, dst=n3), Edge.new(src=n2, dst=n3),
        ...     # The second three-clique.
        ...     Edge.new(src=n4, dst=n5), Edge.new(src=n4, dst=n6), Edge.new(src=n5, dst=n6),
        ...     # The connection between the three-cliques.
        ...     Edge.new(src=n1, dst=n4)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> label_propagation = graph.label_propagation()
        >>> select(node.id, label).where(label_propagation(node, label)).inspect()
        # The output will show each node mapped to a community:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        **Weighted Graph Example**

        Compute community assignments for each node in an undirected weighted
        graph. Here, a six-clique has the edges forming a dumbbell graph
        within the six-clique strongly weighted, and the remaining edges
        weakly weighted. The graph resolves into two communities, namely the
        two three-cliques constituent of the dumbbell embedded in the
        six-clique.

        >>> # 1. Set up a weighted, undirected graph
        >>> model = Model("test_model")
        >>> graph = Graph(model, directed=False, weighted=True)
        >>> Node, Edge = graph.Node, graph.Edge
        >>>
        >>> # 2. Define nodes and edges
        >>> n1, n2, n3, n4, n5, n6 = [Node.new(id=i) for i in range(1, 7)]
        >>> define(n1, n2, n3, n4, n5, n6)
        >>> define(
        ...     # First embedded three-clique.
        ...     Edge.new(src=n1, dst=n2, weight=1.0),
        ...     Edge.new(src=n1, dst=n3, weight=1.0),
        ...     Edge.new(src=n2, dst=n3, weight=1.0),
        ...     # Second embedded three-clique.
        ...     Edge.new(src=n4, dst=n5, weight=1.0),
        ...     Edge.new(src=n4, dst=n6, weight=1.0),
        ...     Edge.new(src=n5, dst=n6, weight=1.0),
        ...     # Slightly weaker connection between the embedded three-cliques.
        ...     Edge.new(src=n1, dst=n4, weight=0.5),
        ...     # Weaker edges connecting the six-clique in full.
        ...     Edge.new(src=n1, dst=n5, weight=0.1), Edge.new(src=n1, dst=n6, weight=0.1),
        ...     Edge.new(src=n2, dst=n4, weight=0.1), Edge.new(src=n2, dst=n5, weight=0.1),
        ...     Edge.new(src=n2, dst=n6, weight=0.1), Edge.new(src=n3, dst=n4, weight=0.1),
        ...     Edge.new(src=n3, dst=n5, weight=0.1), Edge.new(src=n3, dst=n6, weight=0.1)
        ... )
        >>>
        >>> # 3. Compute community assignments and inspect
        >>> node, label = Node.ref("node"), Integer.ref("label")
        >>> label_propagation = graph.label_propagation()
        >>> select(node.id, label).where(label_propagation(node, label)).inspect()
        # The output will show the two-community dumbbell structure:
        # (1, 1)
        # (2, 1)
        # (3, 1)
        # (4, 2)
        # (5, 2)
        # (6, 2)

        """
        _assert_type("label_propagation:max_sweeps", max_sweeps, int)
        _assert_inclusive_lower_bound("label_propagation:max_sweeps", max_sweeps, 0)

        _assert_type("label_propagation:randomization_seed", randomization_seed, int)
        _assert_exclusive_lower_bound("label_propagation:randomization_seed", randomization_seed, 0)

        raise NotImplementedError("`label_propagation` is not yet implemented.")
