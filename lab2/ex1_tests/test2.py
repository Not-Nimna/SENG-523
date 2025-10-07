def outiefunc (a, b):
    c = 30 # <--c is defined, but not used
    d = a + b
    def inniefunc(x, y):
        c = 15 # <--this is a different c!
        return c
    return d






# import ast

# class UsageAnalyzer(ast.NodeVisitor):
#     def __init__(self, target_name):
#         self.target_name = target_name
#         self.defs = set()   # where it's defined
#         self.uses = set()   # where it's used
#         self.scope_stack = []

#     def visit_FunctionDef(self, node):
#         self.scope_stack.append(node.name)
#         self.generic_visit(node)
#         self.scope_stack.pop()

#     def visit_Assign(self, node):
#         for target in node.targets:
#             if isinstance(target, ast.Name) and target.id == self.target_name:
#                 self.defs.add(self.scope_stack[-1] if self.scope_stack else "module")
#         self.generic_visit(node)

#     def visit_Name(self, node):
#         if isinstance(node.ctx, ast.Load) and node.id == self.target_name:
#             self.uses.add(self.scope_stack[-1] if self.scope_stack else "module")
#         self.generic_visit(node)
