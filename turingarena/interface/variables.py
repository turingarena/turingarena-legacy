from collections import namedtuple

from turingarena.interface.statement import Statement
from turingarena.interface.type_expressions import ValueType


class Variable(namedtuple("Variable", ["name", "value_type"])):
    @property
    def metadata(self):
        return dict(
            name=self.name,
            type=self.value_type.metadata,
        )


class VarStatement(Statement):
    __slots__ = []

    @property
    def value_type(self):
        return ValueType.compile(self.ast.type.expression)

    @property
    def variables(self):
        return tuple(
            Variable(value_type=self.value_type, name=d.name)
            for d in self.ast.declarators
        )

    @property
    def context_after(self):
        return self.context.with_variables(self.variables)
