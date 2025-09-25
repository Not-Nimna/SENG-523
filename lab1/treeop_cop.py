import sys
import ast
import zss

# --- Utility Functions (Used by Exercise 2, 3, and 4) ---

def get_children(node):
    if isinstance(node, ast.AST):
        children = []
        for field, value in ast.iter_fields(node):
            if field in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
                continue
            if isinstance(value, list):
                children.extend(value)
            elif isinstance(value, ast.AST):
                children.append(value)
            else:
                children.append(value)
        return children
    elif isinstance(node, list):
        return node
    else:
        return []


def get_label(node):
    if isinstance(node, ast.AST):
        return type(node).__name__
    else:
        return str(node)


# --- Helper for Exercise 3 ---

def count_ast_nodes(node):
    if not isinstance(node, ast.AST):
        return 0
    count = 1
    for child in get_children(node):
        if isinstance(child, ast.AST):
            count += count_ast_nodes(child)
    return count


# --- Exercise 4 Implementation: Program Interpreter ---

class SimpleProgramInterpreter(ast.NodeVisitor):
    def __init__(self):
        self.variables = {}
        self.last_value = None

    def evaluate(self, tree):
        self.visit(tree)
        return self.last_value

    def visit_Module(self, node):
        for statement in node.body:
            self.visit(statement)

    def visit_Assign(self, node):
        value = self.visit(node.value)
        target_name = node.targets[0].id  # fix here
        self.variables[target_name] = value
        self.last_value = value

    def visit_BinOp(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left_val + right_val
        elif isinstance(node.op, ast.Mult):
            return left_val * right_val
        else:
            raise TypeError("Unsupported binary operation.")

    def visit_Constant(self, node):
        return node.value

    def visit_Num(self, node):  # for older Python
        return node.n

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            name = node.id
            if name in self.variables:
                return self.variables[name]
            else:
                raise NameError(f"Variable '{name}' used before assignment.")
        return None


# --- Exercise 2 Implementation ---

def do_cmp(fname1, fname2):
    try:
        with open(fname1, "r") as f1, open(fname2, "r") as f2:
            content1 = f1.read()
            content2 = f2.read()
    except FileNotFoundError:
        print("Error: One or both files not found.")
        return -1

    tree1 = ast.parse(content1, filename=fname1)
    tree2 = ast.parse(content2, filename=fname2)

    def compare(n1, n2):
        if get_label(n1) != get_label(n2):
            return False
        c1, c2 = get_children(n1), get_children(n2)
        if len(c1) != len(c2):
            return False
        for i in range(len(c1)):
            if not compare(c1[i], c2[i]):
                return False
        return True

    if compare(tree1, tree2):
        print("The programs are identical")
        return 0
    else:
        print("The programs are not identical")
        return 1


# --- Exercise 3 Implementation ---

def do_dst(fname1, fname2):
    try:
        with open(fname1, "r") as f1, open(fname2, "r") as f2:
            content1 = f1.read()
            content2 = f2.read()
    except FileNotFoundError:
        print("Error: One or both files not found.")
        return -1

    tree1 = ast.parse(content1, filename=fname1)
    tree2 = ast.parse(content2, filename=fname2)

    distance = zss.simple_distance(
        tree1,
        tree2,
        get_children=get_children,
        get_label=get_label
    )

    N1 = count_ast_nodes(tree1)
    N2 = count_ast_nodes(tree2)
    sum_nodes = N1 + N2
    
    print(N1)
    print(N2)
    print(distance)

    normalized_distance = distance / sum_nodes if sum_nodes > 0 else 0.0
    print(f"The normalized tree edit distance is {normalized_distance}")
    return 0


# --- Exercise 4 Implementation ---

def do_run(fname):
    try:
        with open(fname, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return -1

    tree = ast.parse(content, filename=fname)
    interpreter = SimpleProgramInterpreter()
    try:
        result = interpreter.evaluate(tree)
        print(f"The result is {result}")
        return 0
    except (NameError, TypeError, KeyError) as e:
        print(f"Execution Error: {e}")
        return -1


# --- Main Execution Block ---

def main():
    if len(sys.argv) == 4 and sys.argv[1] == "cmp":
        return do_cmp(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "dst":
        return do_dst(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        return do_run(sys.argv[2])
    else:
        print("Usage: python treeops.py <command> <file1.py> [file2.py]")
        return -1


if __name__ == "__main__":
    main()
