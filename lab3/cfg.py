import ast
from typing import List, Set, Optional, Dict
import sys

# Global counter for BasicBlock IDs
_basic_block_counter = 0

def _next_basic_block_id():
    global _basic_block_counter
    _basic_block_counter += 1
    return f"BB{_basic_block_counter}"

def open_file(fname):
    with open(fname, "r") as f1:
        file1 = f1.read()
        tree = ast.parse(file1, filename=fname)
        return tree
    
def get_used_vars(node):
    used = set()
    for subnode in ast.walk(node):
        if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Load):
            used.add(subnode.id)
    return used

class StatementType:
    ASSIGNMENT = "assignment"
    IF = "if"
    WHILE = "while"
    PRINT = "print"
    RETURN = "return"
    OTHER = "other"

class Statement:
    def __init__(self, stmt_type: str, def_set: Set[str], use_set: Set[str], ast_node: ast.AST):
        self.stmt_type: str = stmt_type
        self.def_set: Set[str] = def_set
        self.use_set: Set[str] = use_set
        self.ast_node: ast.AST = ast_node

class BasicBlock:
    def __init__(self):
        self.id: str = _next_basic_block_id()
        self.statements: List[Statement] = []
        self.def_set: Set[str] = set()
        self.use_set: Set[str] = set()
        self.predecessors: Set['BasicBlock'] = set()
        self.successors: Set['BasicBlock'] = set()

    def add_statement(self, stmt: Statement):
        self.statements.append(stmt)
        self.def_set.update(stmt.def_set)
        self.use_set.update(stmt.use_set)
    
    def print_bb(self):
        print(f"Basic Block {self.id}")

class EntryBlock(BasicBlock):
    def __init__(self):
        # Don't increment counter
        self.id = "BB0"
        self.statements = []
        self.def_set = set()
        self.use_set = set()
        self.predecessors = set()
        self.successors = set()
        self.label = "Entry"

    def print_bb(self):
        print(f"Basic Block {self.id}: {self.label}")


class ExitBlock(BasicBlock):
    def __init__(self):
        super().__init__()
        self.label = "Exit"

class ControlFlowGraph:
    def __init__(self):
        self.blocks: Set[BasicBlock] = set()
        self.entry: EntryBlock = EntryBlock()
        self.exit: Optional[ExitBlock] = None
        self.blocks.add(self.entry)

    def add_block(self, block: BasicBlock):
        self.blocks.add(block)

    def add_edge(self, from_block: BasicBlock, to_block: BasicBlock):
        from_block.successors.add(to_block)
        to_block.predecessors.add(from_block)
    
    def print_cfg(self):
        # self.entry.print_bb()

        for bb in self.blocks:
            bb.print_bb()

        # self.exit.print_bb()



def make_cfg(ast_node: ast.AST) -> ControlFlowGraph:
    """
    Constructs a Control Flow Graph (CFG) from the given AST node (tree or subtree).
    Returns a ControlFlowGraph instance representing the CFG.
    """
    cfg = ControlFlowGraph()
    current_block = BasicBlock()
    cfg.add_block(current_block)
    cfg.add_edge(cfg.entry, current_block)

    for node in ast.walk(ast_node):
        if isinstance(node, (ast.Assign)):
            def_set = set()
            # get the set of used variables
            use_set = get_used_vars(node.value)

            # get the set of defined variables
            for target in node.targets:
                for subnode in ast.walk(target):
                    if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Store):
                        def_set.add(subnode.id)

            stmt_block = Statement(StatementType.ASSIGNMENT, def_set, use_set, node)
            current_block.add_statement(stmt_block)
            

        # elif isinstance(node, ast.Expr):
        #     pass

        # elif isinstance(node, ast.If):
        #     pass
            
        # elif isinstance(node, ast.While):
        #     pass

        # elif isinstance(node, ast.Return):
        #     pass

    cfg.exit = ExitBlock()
    cfg.exit.id = f"BB{_basic_block_counter + 1}"  # last ID
    cfg.add_block(cfg.exit)
    cfg.add_edge(current_block, cfg.exit)


    return cfg


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "CFG":
        return do_CFG(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "liveness":
        return do_liveness(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "reaching":
        return do_reaching(sys.argv[2])
    else:
        print("Usage: python cfg.py <cmd> <file>")
        return -1
    
# Exercise 1
def do_CFG(fname):
    # read in the AST
    tree = open_file(fname)

    cfg = make_cfg(tree)

    cfg.print_cfg()
    

# Exercise 2
def do_liveness(fname):
    tree = open_file(fname)
    #create CFG
    cfg = make_cfg(tree)

    blocks = []
    # entry first
    blocks.append(cfg.entry)
    # middle blocks sorted by id
    real_blocks = [b for b in cfg.blocks if not isinstance(b, (EntryBlock, ExitBlock))]
    real_blocks = sorted(real_blocks, key=lambda b: b.id)
    blocks.extend(real_blocks)
    # exit last
    blocks.append(cfg.exit)
    #lists
    in_list = [set() for _ in blocks]
    out_list = [set() for _ in blocks]
    #list all the blocks
    all_blocks = []
    for block in blocks:
        all_blocks.append(block)

    #loop
    while len(all_blocks)> 0:
        #entry
        current = all_blocks.pop(0)
        i = blocks.index(current)

        # out set with union in sets
        new_out = set()
        for succ in current.successors:
            if succ in blocks:
                j = blocks.index(succ)
                new_out = new_out.union(in_list[j])

        # in set 
        new_in = set(current.use_set)
        for a in new_out:
            if a not in current.def_set:
                new_in.add(a)
        
        # check in set for changes
        if new_in != in_list[i]:
            in_list[i] = new_in
            out_list[i] = new_out
             # add predecessors to the list
            for pred in current.predecessors:
                if pred not in all_blocks:
                    all_blocks.append(pred)
        else:
            out_list[i] = new_out

    #Ensure Final blocks are correct
    used = set()
    final_blocks = []
    for b in blocks:
        if b.id not in used:
            final_blocks.append(b)
            used.add(b.id)

    #print results
    for b in final_blocks:
        idx = blocks.index(b)
        prednames = [p.id for p in b.predecessors]
        succnames = [s.id for s in b.successors]

        is_entry = len(prednames) == 0
        is_exit = len(succnames) == 0
        is_mid = 0

        if is_entry:
            print("Basic Block", b.id, ": Entry")
        elif is_exit:
            print("Basic Block", b.id, ": Exit")
        else:
            print("Basic Block", b.id, ":")
            is_mid = 1
        if is_mid:    
            # defs
            print("defs:", end=" ")
            if len(b.def_set) == 0:
                print()
            else:
                print(" ".join(sorted(b.def_set)))
            # uses
            print("uses:", end=" ")
            if len(b.use_set) == 0:
                print()
            else:
                print(" ".join(sorted(b.use_set)))
            # in
            print("in:", end=" ")
            if len(in_list[idx]) == 0:
                print()
            else:
                print(" ".join(sorted(in_list[idx])))
            # out
            print("out:", end=" ")
            if len(out_list[idx]) == 0:
                print()
            else:
                print(" ".join(sorted(out_list[idx])))

        # preds
        print("Predecessors:", end=" ")
        if len(prednames) == 0:
            print()
        else:
            print(" ".join(prednames))
        # succs
        print("Successors:", end=" ")
        if len(succnames) == 0:
            print()
        else:
            print(" ".join(succnames))
        print()

# Exercise 3
def do_reaching(fname):
    tree = open_file(fname)
    


if __name__ == "__main__":
    main()
