from __future__ import annotations

from dataclasses import dataclass
from relationalai.semantics.metamodel import ir, compiler as c, visitor as v, builtins
from relationalai.semantics.metamodel.util import OrderedSet, ordered_set


class FDConstraints(c.Pass):
    """
    Pass marks all appropriate relations with `function` annotation.
    Criteria:
    - there is a Require node with `unique` builtin (appeared as a result of `require(unique(...))`)
    - `unique` declared for all the fields in a derived relation expect the last
    """

    def rewrite(self, model: ir.Model, options: dict = {}) -> ir.Model:
        collect_fd = CollectFunctionalRelationsVisitor()
        new_model = collect_fd.walk(model)
        # mark relations collected by previous visitor with `@function` annotation
        return FDConstraintsVisitor(collect_fd.functional_relations).walk(new_model)


@dataclass
class CollectFunctionalRelationsVisitor(v.Rewriter):
    """
    Visitor collects all relations which should be marked with `functional` annotation.
    """

    def __init__(self):
        super().__init__()
        self.functional_relations = ordered_set()

    def handle_check(self, node: ir.Check, parent: ir.Node):
        check = self.walk(node.check, node)
        assert isinstance(check, ir.Logical)
        unique_vars = []
        for item in check.body:
            # collect vars from `unique` builtin
            if isinstance(item, ir.Lookup) and item.relation.name == builtins.unique.name:
                var_set = set()
                for vargs in item.args:
                    assert isinstance(vargs, tuple)
                    var_set.update(vargs)
                unique_vars.append(var_set)
        functional_rel = []
        # mark relations as functional when at least 1 `unique` builtin
        if len(unique_vars) > 0:
            for item in check.body:
                if isinstance(item, ir.Lookup) and not item.relation.name == builtins.unique.name:
                    for var_set in unique_vars:
                        # when unique declared for all the fields except the last one in the relation mark it as functional
                        if var_set == set(item.args[:-1]):
                            functional_rel.append(item.relation)

        self.functional_relations.update(functional_rel)
        return node.reconstruct(check, node.error, node.annotations)


@dataclass
class FDConstraintsVisitor(v.Rewriter):
    """
    This visitor marks functional_relations with `functional` annotation.
    """

    def __init__(self, functional_relations: OrderedSet):
        super().__init__()
        self._functional_relations = functional_relations

    def handle_relation(self, node: ir.Relation, parent: ir.Node):
        if node in self._functional_relations:
            return node.reconstruct(node.name, node.fields, node.requires, node.annotations | [builtins.function_checked_annotation],
                                    node.overloads)
        return node.reconstruct(node.name, node.fields, node.requires, node.annotations, node.overloads)

    def handle_update(self, node: ir.Update, parent: ir.Node):
        if node.relation in self._functional_relations:
            return node.reconstruct(node.engine, node.relation, node.args, node.effect,
                                    node.annotations | [builtins.function_checked_annotation])
        return node.reconstruct(node.engine, node.relation, node.args, node.effect, node.annotations)
