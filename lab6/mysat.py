import sys
import ast
from graphviz import Digraph

class LogicNode:
    def __init__(self, ntype, nsym):
        # Possible ntype values are AND, OR, NOT, IMPL
        self.ntype = ntype
        self.nsym = nsym
        self.op1 = None
        self.op2 = None

    def to_string(self, indent_level=0, node_str=None):
        if not node_str:
            node_str = ""
        node_str += (" " * indent_level)
        if self.ntype != "SYM":
            node_str += (f"{self.ntype} OPERATOR\n")
        else:
            node_str += (f"{self.nsym} SYMBOL\n")
        if self.op1:
            node_str = self.op1.to_string(indent_level+2, node_str)
        if self.op2:
            node_str = self.op2.to_string(indent_level+2, node_str)
        return node_str


class TreeVisualizer:
    def __init__(self):
        self.node_counter = 0
        try:
            self.graph = Digraph('Tree')
        except ImportError:
            print("Error: graphviz module not found. Please install it with 'pip install graphviz'")
            sys.exit(1)
    
    def add_node(self, label=None):
        """Add a node to the graph and return its ID"""
        node_id = f"node{self.node_counter}"
        self.node_counter += 1
        
        if label is None:
            label = node_id
        
        self.graph.node(node_id, label)
        return node_id
    
    def add_edge(self, parent_id, child_id):
        """Add an edge between two nodes"""
        self.graph.edge(parent_id, child_id)
    
    def render(self, output_file):
        """Render the graph to a PNG file"""
        try:
            # Remove .png extension if present, graphviz will add it
            base_name = output_file.replace('.png', '')
            self.graph.render(base_name, format='png', cleanup=True)
            print(f"Tree rendered to {output_file}")
        except Exception as e:
            print(f"Error rendering graph: {e}")



def ast_to_logic(pynode):
    # Handle symbols
    if isinstance(pynode, ast.Name):
        return LogicNode("SYM", pynode.id)
    
    # Handle Function calls
    if isinstance(pynode, ast.Call):
        func1 = pynode.func.id
        node = LogicNode(func1, None)

        if func1 == "NOT":
            node.op1 = ast_to_logic(pynode.args[0])
        else:
            node.op1 = ast_to_logic(pynode.args[0])
            node.op2 = ast_to_logic(pynode.args[1])
        return node
    raise Exception(f"Incorrect AST: {type(pynode)}")



def main():
    if len(sys.argv) != 3:
        print("Usage: python mysat.py <operation> <input_file>")
        sys.exit(1)
    elif sys.argv[1] == "parse":
        parse(sys.argv[2])
    elif sys.argv[1] == "visualize":
        visualize(sys.argv[2])
    elif sys.argv[1] == "evaluate":
        evaluate(sys.argv[2])
    elif sys.argv[1] == "solve":
        solve(sys.argv[2])
    else:
        print("Usage: python mysat.py <operation> <input_file>")
        sys.exit(1)

def parse(input_file):
    with open(input_file, 'r') as f:
        content = f.read().strip()
    py_ast = ast.parse(content, mode='eval')
    logic_tree = ast_to_logic(py_ast.body)

    #render
    print(logic_tree.to_string())
    return logic_tree


def visualize(input_file):
    tree = parse(input_file)
    visualizer = TreeVisualizer()
    def create(node):
        label = node.nsym if node.ntype == "SYM" else node.ntype
        node_id = visualizer.add_node(label)
        if node.op1:
            child1_id = create(node.op1)
            visualizer.add_edge(node_id, child1_id)
        if node.op2:
            child2_id = create(node.op2)
            visualizer.add_edge(node_id, child2_id)
        return node_id
    create(tree)
    visualizer.render("output.png")


def evaluate(input_file):
    with open(input_file, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    # Last line is formula
    formula_text = lines[-1]
    assignments = {}

    for line in lines[:-1]:
        name, value = line.split("=")
        name = name.strip()
        value = value.strip()
        assignments[name] = (value == "True")

    # Parse the formula
    py_ast = ast.parse(formula_text, mode='eval')
    logic_tree = ast_to_logic(py_ast.body)

    # Recursive evaluation
    def eval_node(node):
        if node.ntype == "SYM":
            return assignments[node.nsym]

        if node.ntype == "NOT":
            return not eval_node(node.op1)

        if node.ntype == "AND":
            return eval_node(node.op1) and eval_node(node.op2)

        if node.ntype == "OR":
            return eval_node(node.op1) or eval_node(node.op2)

        if node.ntype == "IMPL":
            return (not eval_node(node.op1)) or eval_node(node.op2)

        raise ValueError("Unknown operator")

    result = eval_node(logic_tree)
    print(f"The formula evaluates to {result}")
    return result



def solve(input_file):
    with open(input_file, "r") as f:
        content = f.read().strip()
    
    py_ast = ast.parse(content, mode='eval')
    logic_tree = ast_to_logic(py_ast.body)

    # Get all symbols
    symbols = []

    def collect(node):
        if node.ntype == "SYM":
            if node.nsym not in symbols:
                symbols.append(node.nsym)
        if node.op1:
            collect(node.op1)
        if node.op2:
            collect(node.op2)

    collect(logic_tree)

    def eval_node(node, env):
        if node.ntype == "SYM":
            return env[node.nsym]
        if node.ntype == "NOT":
            return not eval_node(node.op1, env)
        if node.ntype == "AND":
            return eval_node(node.op1, env) and eval_node(node.op2, env)
        if node.ntype == "OR":
            return eval_node(node.op1, env) or eval_node(node.op2, env)
        if node.ntype == "IMPL":
            return (not eval_node(node.op1, env)) or eval_node(node.op2, env)
        raise ValueError("Unknown operator")
    
    i = len(symbols)

    # Try all combinations
    def make_combinations(symbols):
        if not symbols:
            return [ {} ]

        first = symbols[0]
        rest = symbols[1:]

        sub = make_combinations(rest)
        result = []

        for a in sub:
            env_false = a.copy()
            env_false[first] = False
            result.append(env_false)

            env_true = a.copy()
            env_true[first] = True
            result.append(env_true)

        return result

    combinations = make_combinations(symbols)
    for env in combinations:
        if eval_node(logic_tree, env):
            parts = [f"{s}: {env[s]}" for s in symbols]
            print("SAT: " + ", ".join(parts))
            return
    # If no combination worked
    print("UNSAT")


if __name__ == "__main__":
    main()
