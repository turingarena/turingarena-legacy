from turingarena.interfaces.analysis.block import compile_block, BlockContext
from turingarena.interfaces.analysis.declaration import compile_declaration
from turingarena.interfaces.analysis.scope import Scope


class InterfaceCompiler:
    def compile(self, interface):
        interface.variable_declarations = []
        interface.function_declarations = []
        interface.callback_declarations = []
        compiler = InterfaceItemCompiler(interface)
        for item in interface.interface_items:
            item.interface = interface
            item.accept(compiler)


class InterfaceItemCompiler:
    def __init__(self, interface):
        self.interface = interface
        self.global_scope = Scope()

    def visit_variable_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.variable_declarations.append(declaration)

    def visit_function_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.function_declarations.append(declaration)

    def visit_callback_declaration(self, declaration):
        compile_declaration(declaration, scope=self.global_scope)
        self.interface.callback_declarations.append(declaration)

    def visit_main_declaration(self, declaration):
        compile_block(declaration.block, context=BlockContext(True), scope=self.global_scope)