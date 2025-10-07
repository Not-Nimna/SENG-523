import sys
import ast
import re


def open_file(fname):
    with open(fname, "r") as f1:
        file1 = f1.read()
        tree = ast.parse(file1, filename=fname)
        return tree


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "unused":
        return do_unused(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "returns":
        return do_returns(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "constant":
        return do_constant(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "secret":
        return do_secret(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "taint":
        return do_taint(sys.argv[2])
    else:
        print("Usage: python astanalysis.py <cmd> <file>")
        return -1
    
# Exercise 1
def do_unused(fname):

    tree = open_file(fname)

    class VarUsageAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.scope_stack = []
            self.messages = []

        def visit_FunctionDef(self, node: ast.FunctionDef):
            current_scope = {"name": node.name, "vars": {}}
            self.scope_stack.append(current_scope)
            self.generic_visit(node)
            scope = self.scope_stack.pop()
            for v, st in scope["vars"].items():
                if st["defined"] and not st["used"]:
                    self.messages.append(
                        f"Variable {v} is defined but not used in scope {scope['name']}"
                    )

        def visit_Assign(self, node: ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    varname = target.id
                    if self.scope_stack:
                        scope = self.scope_stack[-1]
                        for outer in self.scope_stack[:-1]:
                            if varname in outer["vars"]:
                                self.messages.append("Variable " + varname + " is shadowed across scopes")

                        scope["vars"].setdefault(varname, {"defined": True, "used": False})
            self.generic_visit(node)

        def visit_Name(self, node: ast.Name):
            if isinstance(node.ctx, ast.Load):  # variable read
                for scope in reversed(self.scope_stack):
                    if node.id in scope["vars"]:
                        scope["vars"][node.id]["used"] = True
                        break
            self.generic_visit(node)

        def report(self):
            for msg in self.messages:
                print(msg)
            
    analyzer = VarUsageAnalyzer()
    analyzer.visit(tree)
    analyzer.report()


       
# Exercise 2
def do_returns(fname):

    tree = open_file(fname)
    class ReturnChecker(ast.NodeVisitor):
        def __init__(self):
            self.messages = []

        def visit_FunctionDef(self, node: ast.FunctionDef):
            if not self.contains_return(node.body):
                self.messages.append(
                    f"Function {node.name} is missing a return statement"
                )

            self.check_block(node.body, node.name)
            self.generic_visit(node)

        def check_block(self, stmts, funcname):
            for stmt in stmts:
                if isinstance(stmt, ast.If):
                    has_ret_if = self.contains_return(stmt.body)
                    has_ret_else = self.contains_return(stmt.orelse)

                    if not has_ret_if or not has_ret_else:
                        self.messages.append(
                            f"Function {funcname} is missing a return statement"
                        )
                    self.check_block(stmt.body, funcname)
                    self.check_block(stmt.orelse, funcname)

        def contains_return(self, stmts):
            for st in stmts:
                if isinstance(st, ast.Return):
                    return True
                if isinstance(st, ast.If):
                    if self.contains_return(st.body) or self.contains_return(st.orelse):
                        return True
            return False
        
    checker = ReturnChecker()
    checker.visit(tree)
    for msg in checker.messages:
        print(msg)




# Exercise 3
def do_constant(fname):
    # python astanalysis.py constant test.py

    tree = open_file(fname)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.If):

            # constant condition
            if isinstance(node.test, ast.Constant):
                print("Conditional statement with constant condition detected")


            # check comparison
            elif isinstance(node.test, ast.Compare):
                lhs_rhs = [node.test.left] + node.test.comparators

                if all(isinstance(val, ast.Constant) for val in lhs_rhs):

                    print("Conditional statement with constant condition detected")

    return 0


# Exercise 4
def do_secret(fname):

    variable_name_regex = re.compile(r"(secret|password|key|token)")

    variable_value_regex =  re.compile(r"^WOWSECRET_\d{2,5}_[A-Z]{4}$")

    tree = open_file(fname)
    variables = {}
    sus_variables = {}
    def get_unique_load_variables(tree_node_pointer): 

        
        for node in ast.walk(tree_node_pointer):
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name):
                    varname = node.targets[0].id
                    if isinstance(node.value, ast.Constant):
                        variables[varname] = node.value.value
                        
    get_unique_load_variables(tree)

    for key,val in variables.items():
        if variable_name_regex.search(key) and variable_value_regex.search(val):
            sus_variables[key] = val

    if sus_variables:
        for key,val in sus_variables.items():
            print(f"Variable {key} assigned possible secret {val}")


# Exercise 5
def do_taint(fname):
    # python astanalysis.py taint test.py
    tree = open_file(fname)

    tainted = {} # keep track of tainted variables
    danger = False # boolean to track unsafe data flows

    def is_tainted(node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            # Test functions
            if node.func.id == "input":
                return True
            if node.func.id == "sanitized": # always untainted
                return False
            # Check arguments
            return any(is_tainted(arg) for arg in node.args)
        
        # Tracking binary operations
        if isinstance(node, ast.BinOp):
            # test both sides of operation
            return is_tainted(node.left) or is_tainted(node.right)
        
        # Tracking variables
        if isinstance(node, ast.Name):
            return tainted.get(node.id, False)
        
        return False

    # For any assignments
    for node in ast.walk(tree):
        # update any tainted vars through assignments
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                tainted[node.targets[0].id] = is_tainted(node.value)
    
    # Check os.system calls for taints
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "system":
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "os":
                            for arg in node.args:
                                if is_tainted(arg):
                                    print("Unsafe data flow between source and sink detected")
                                    danger = True
    return 0

if __name__ == "__main__":
    main()
