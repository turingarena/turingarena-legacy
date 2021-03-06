from turingarena.driver.common.nodes import *
from turingarena.util.visitor import visitormethod


class TreeTransformer:
    def transform_all(self, ns):
        return tuple(self.transform(n) for n in ns)

    @visitormethod
    def transform(self, n):
        pass

    def transform_object(self, n):
        return n

    def transform_Call(self, n):
        return n._replace(
            callbacks=self.transform_all(n.callbacks)
        )

    def transform_Callback(self, n):
        return n._replace(
            body=self.transform(n.body),
        )

    def transform_Interface(self, n):
        return n._replace(
            constants=self.transform_all(n.constants),
            methods=self.transform_all(n.methods),
            main=self.transform(n.main),
        )

    def transform_For(self, n):
        return n._replace(
            index=self.transform(n.index),
            body=self.transform(n.body),
        )

    def transform_If(self, n):
        return n._replace(
            condition=self.transform(n.condition),
            branches=IfBranches(*self.transform_all(n.branches)),
        )

    def transform_Switch(self, n):
        return n._replace(
            value=self.transform(n.value),
            cases=self.transform_all(n.cases),
        )

    def transform_Case(self, n):
        return n._replace(
            body=self.transform(n.body),
        )

    def transform_Loop(self, n):
        return n._replace(
            body=self.transform(n.body),
        )

    def transform_Block(self, n):
        return n._replace(
            children=self.transform_all(n.children),
        )
