import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, Allocation, ReferenceStatus

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(Statement, Instruction):
    __slots__ = []

    @property
    def index(self):
        return ForIndex(
            variable=Variable(name=self.ast.index, dimensions=0),
            range=Expression.compile(self.ast.range, self.context),
        )

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.with_index_variable(self.index),
        )

    def _get_allocations(self):
        for step in self.body.instructions:
            for inst in step.instructions:
                for a in inst.reference_actions:
                    if a.reference.variable.dimensions == 0:
                        continue
                    if a.status == ReferenceStatus.DECLARED:
                        yield Allocation(
                            reference=a.reference._replace(
                                index_count=a.reference.index_count - 1,
                            ),
                            size=self.index.range,
                        )

    def _get_instructions(self):
        yield self

    def validate(self):
        yield from self.body.validate()

    @property
    def may_process_requests(self):
        return self.body.may_process_requests

    def expects_request(self, request):
        return (
            request is None
            or self.body.expects_request(request)
        )

    def _get_direction(self):
        return self.body.direction

    def _get_reference_actions(self):
        for a in self.body.reference_actions:
            r = a.reference
            if r.index_count > 0:
                yield a._replace(reference=r._replace(index_count=r.index_count - 1))
