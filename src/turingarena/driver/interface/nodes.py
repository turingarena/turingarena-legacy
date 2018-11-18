from collections import namedtuple
from typing import List, Mapping, Any

from turingarena.driver.interface.variables import ReferenceAction, Reference, ReferenceStatus, VariableDeclaration

Bindings = Mapping[Reference, Any]


class ExecutionResult(namedtuple("ExecutionResult", [
    "assignments",
    "request_lookahead",
    "does_break",
])):
    def merge(self, other):
        if other is None:
            return self

        return ExecutionResult(
            self.assignments + other.assignments,
            request_lookahead=other.request_lookahead,
            does_break=other.does_break,
        )

    def with_request_processed(self):
        return self._replace(request_lookahead=None)


class IntermediateNode:
    __slots__ = []

    def validate(self):
        return []

    @property
    def variable_declarations(self):
        return frozenset(self._get_variable_declarations())

    def _should_declare_variables(self):
        return False

    def _get_variable_declarations(self):
        if not self._should_declare_variables():
            return
        for a in self.reference_actions:
            if a.reference.index_count == 0 and a.status == ReferenceStatus.DECLARED:
                yield VariableDeclaration(a.reference.variable)

    @property
    def variable_allocations(self):
        return list(self._get_allocations())

    def _get_allocations(self):
        return []

    @property
    def comment(self):
        return self._get_comment()

    def _get_comment(self):
        return None

    @property
    def is_relevant(self):
        "Whether this node should be kept in the parent block"
        return self._is_relevant()

    def _is_relevant(self):
        return True

    @property
    def reference_actions(self) -> List[ReferenceAction]:
        """
        List of references involved in this instruction.
        """
        actions = list(self._get_reference_actions())
        assert all(isinstance(a, ReferenceAction) for a in actions)
        return actions

    def _get_reference_actions(self):
        return []

    @property
    def declaration_directions(self):
        return frozenset(self._get_declaration_directions())

    def _get_declaration_directions(self):
        return frozenset()

    @property
    def can_be_grouped(self):
        return self._can_be_grouped()

    def _can_be_grouped(self):
        return True

    @property
    def node_description(self):
        return list(self._describe_node())

    @staticmethod
    def _indent_all(lines):
        for l in lines:
            yield "  " + l

    def _describe_node(self):
        yield str(self)
