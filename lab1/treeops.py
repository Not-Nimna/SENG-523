from platform import node
import sys
import ast
import zss
from zss import Node, simple_distance

def main():
    if len(sys.argv) == 4 and sys.argv[1] == "cmp":
        return do_cmp(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "dst":
        return do_dst(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        return do_run(sys.argv[2])
    else:
        print("Usage: python treeops.py <cmd> <file 1> <optional file 2>")
        return -1

# opening files

def open_files(fname1, fname2):
    with open(fname1, "r") as f1, open(fname2, "r") as f2:
        file1 = f1.read()
        file2 = f2.read()
        tree1 = ast.parse(file1, filename=fname1)
        tree2 = ast.parse(file2, filename=fname2)
        return tree1,tree2

        
# Provide the solution to Exercise 2 by implementing the function below
def do_cmp(fname1, fname2):
    # Generate ASTS
    tree1,tree2 = open_files(fname1, fname2)

    def cmpASTs(node1, node2):
        # Compare AST nodes
        if isinstance(node1, ast.AST) and isinstance(node2, ast.AST):
            if type(node1) is not type(node2):
                return False
            for (field, value) in ast.iter_fields(node1):
                if not cmpASTs(value, getattr(node2, field)):
                    return False
            return True
        # Compare lists
        if isinstance(node1, list) and isinstance(node2, list):
            if len(node1) != len(node2):
                return False
            for a,b in zip(node1, node2):
                if not cmpASTs(a, b):
                    return False
            return True
        # For strings/numbers
        return node1 == node2
    # Commpare ASTs of both files
    if cmpASTs(tree1, tree2):
        print("The programs are identical")
    else:
        print("The programs are not identical")

# Provide the solution to Exercise 3 by implementing the function below
def do_dst(fname1, fname2):
    tree1,tree2 = open_files(fname1, fname2)

    # only counting name, constant and attr nodes
    def node_label(node, include_values=True):
        type_of_node = type(node).__name__
        if not include_values:
            return type_of_node
        if isinstance(node, ast.Name):
            return f"Name:{node.id}:{type(node.ctx).__name__}"
        if isinstance(node, ast.Constant):
            return f"Const:{repr(node.value)}"
        if isinstance(node, ast.Attribute):
            return f"Attribute:{node.attr}"
        if isinstance(node, ast.arg):
            return f"arg:{node.arg}"
        return type_of_node

    # iterating over children
    def node_children(node, ignore_ctx=True):
        for c in ast.iter_child_nodes(node):
            if ignore_ctx and isinstance(c, ast.expr_context):
                continue
            yield c

    # converting to the zss AST structure
    def ast_to_zss_tree(node, *, include_values=True, ignore_ctx=True):
        z = Node(node_label(node, include_values))
        for child in node_children(node, ignore_ctx):
            z.addkid(ast_to_zss_tree(child, include_values=include_values, ignore_ctx=ignore_ctx))
        return z
    
    # counting the nodes to normalize
    def count_nodes(node: Node):
        # adding 1 caus when we start from root we skip the module node
        return 1 + sum(count_nodes(c) for c in Node.get_children(node))

    z_tree_1 = ast_to_zss_tree(tree1, include_values=True, ignore_ctx=True)
    z_tree_2 = ast_to_zss_tree(tree2, include_values=True, ignore_ctx=True)
    node_sum_1 = count_nodes(z_tree_1)
    node_sum_2 = count_nodes(z_tree_2)

    distance = simple_distance(z_tree_1, z_tree_2)
    print(f"node sum for 1 is {node_sum_1}")
    print(f"node sum for 2 is {node_sum_2}")
    print(f"node sum for simple_distance is {distance}")

    print(f'The normalized tree edit distance is {distance / (node_sum_1 + node_sum_2)}')

# Provide the solution to Exercise 4 by implementing the function below
def do_run(fname):

    with open(fname, "r") as f1:
        file1 = f1.read()
        tree = ast.parse(file1, filename=fname)

    # temp dict to store variables
    temp_dict = {}

    def calculate_ast(node):
        # if base node is root    
        if isinstance(node, ast.Module):
            result = None
            for stmt in node.body:
                result = calculate_ast(stmt)
            return result
        
        # if node is assigning value recursive call to get value
        elif isinstance(node, ast.Assign):
            target = node.targets[0].id
            value = calculate_ast(node.value)
            # once we get value we have the key in dictionary then assign value to key
            temp_dict[target] = value
            return value
        
        # if expression recirsive call
        elif isinstance(node, ast.Expr):
            return calculate_ast(node.value)
        
        # if its a binOB get left and right and only do sum and multiply
        elif isinstance(node, ast.BinOp):
            left_val = calculate_ast(node.left)
            right_val = calculate_ast(node.right)

            if isinstance(node.op, ast.Add):
                return left_val + right_val
            elif isinstance(node.op, ast.Sub):
                return left_val - right_val
            elif isinstance(node.op, ast.Mult):
                return left_val * right_val

        # if constant just return value
        elif isinstance(node, ast.Constant):
                return node.value

        # if name just add to dictionary
        elif isinstance(node, ast.Name):
            return temp_dict[node.id]

    calculate_ast(tree)
    last_key = list(temp_dict.keys())[-1]
    last_value = temp_dict[last_key]
    print(f"The result is {last_value}")


if __name__ == "__main__":
    main()
