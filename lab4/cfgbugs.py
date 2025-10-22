import sys
import ast
from typing import List, Set, Optional, Tuple
from collections import deque


def open_file(fname):
    with open(fname, "r") as f1:
        file1 = f1.read()
        tree = ast.parse(file1, filename=fname)
        return tree
    

##################################################################################################################################################################################################################################################################


class BasicBlock:
    def __init__(self):
        self.id = None
        self.label = ""
        self.successors = []

class ControlFlowGraph:
    def __init__(self):
        self.blocks = []
        self.edges = []
        self.entry = self.new_block()   # BB0
        self.exit = None

    def new_block(self):
        bb = BasicBlock()
        bb.id = len(self.blocks)
        self.blocks.append(bb)
        return bb

    def add_edge(self, src, dst):
        self.edges.append((src, dst))
        src.successors.append(dst)

    def ensure_exit(self):
        if self.exit is None:
            self.exit = self.new_block()
        return self.exit

def label_for_stmt(node: ast.AST) -> str:
    if isinstance(node, ast.If):
        return f"if {ast.unparse(node.test)}"
    if isinstance(node, ast.Return):
        return f"return {ast.unparse(node.value) if node.value else ''}".strip()
    if isinstance(node, ast.Assign):
        return f"{', '.join(ast.unparse(t) for t in node.targets)} = {ast.unparse(node.value)}"
    if isinstance(node, ast.While):
        return f"while {ast.unparse(node.test)}"
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        return f"{ast.unparse(node.value.func)}(...)"

    return node.__class__.__name__

def make_cfg_for_function(tree: ast.AST):
    func_node = tree.body[0]
    assert isinstance(func_node, ast.FunctionDef)

    cfg = ControlFlowGraph()
    cfg.entry.label = "entry"

    tails = build_from_stmt_list(cfg, func_node.body, cfg.entry)

    exit_bb = cfg.ensure_exit()
    exit_bb.label = "exit"
    for tail in tails:
        if tail is not None:
            cfg.add_edge(tail, exit_bb)
    return cfg

def build_from_stmt_list(cfg, stmts, start_bb):

    tails = [start_bb]

    for stmt in stmts:
 
        if isinstance(stmt, ast.If):
            cond_bb = cfg.new_block()
            cond_bb.label = label_for_stmt(stmt)
            cond_bb.node = stmt
            for t in tails:
                cfg.add_edge(t, cond_bb)

            # good branch
            if stmt.body:  
                true_tails = build_from_stmt_list(cfg, stmt.body, cond_bb)
            else:          
                true_tails = [cond_bb]

            # broewken branch
            if stmt.orelse:  
                false_tails = build_from_stmt_list(cfg, stmt.orelse, cond_bb)
            else:            
                false_tails = [cond_bb]

            tails = true_tails + false_tails


        elif isinstance(stmt, ast.While):
            loop_hdr = cfg.new_block()
            loop_hdr.label = label_for_stmt(stmt)
            loop_hdr.node = stmt
            for t in tails:
                cfg.add_edge(t, loop_hdr)

            if stmt.body:
                body_tails = build_from_stmt_list(cfg, stmt.body, loop_hdr)
                for bt in (body_tails or [loop_hdr]):
                    cfg.add_edge(bt, loop_hdr)  
            else:
                cfg.add_edge(loop_hdr, loop_hdr)

            tails = [loop_hdr]

        elif isinstance(stmt, ast.Return):
            ret_bb = cfg.new_block()
            ret_bb.label = label_for_stmt(stmt)
            ret_bb.node = stmt
            for t in tails:
                cfg.add_edge(t, ret_bb)
            tails = []  
        else:
            stmt_bb = cfg.new_block()
            stmt_bb.label = label_for_stmt(stmt)
            stmt_bb.node = stmt
            for t in tails:
                cfg.add_edge(t, stmt_bb)
            tails = [stmt_bb]

    return tails

def enumerate_blocks(cfg):
    return "\n".join(f'BB{bb.id} = "{bb.label or "block"}"' for bb in cfg.blocks)

def print_cfg(cfg):
    print(enumerate_blocks(cfg))
    print("\nEdges:")
    for src, dst in cfg.edges:
        print(f"  BB{src.id} → BB{dst.id}")

def mark_blocks_reaching_exit_without_return(cfg):
    preds = {bb: [] for bb in cfg.blocks}
    for src, dst in cfg.edges:
        preds[dst].append(src)

    def is_return(bb):
        return isinstance(bb.label, str) and bb.label.startswith("return")

    q = deque([cfg.exit])
    reachable = set([cfg.exit])

    while q:
        bb = q.popleft()
        for p in preds[bb]:
            if p not in reachable and not is_return(p):
                reachable.add(p)
                q.append(p)

    for bb in cfg.blocks:
        if bb is cfg.exit:
            continue
        if bb in reachable:
            reachable_list = sorted(reachable, key=lambda bb: bb.id)
            if reachable_list:  # make sure it's not empty
                last_bb = reachable_list[-2]
                print(f"BB{last_bb.id}: there exists a path to exit without return")
                return

#############################################################################################################################################
# 


def _collect_vars(node: ast.AST) -> Set[str]:
    """Collect variable names (ast.Name loads) used inside an expression."""
    vars_used: Set[str] = set()
    class V(ast.NodeVisitor):
        def visit_Name(self, n: ast.Name):
            if isinstance(n.ctx, ast.Load):
                vars_used.add(n.id)
    if node is not None:
        V().visit(node)
    return vars_used

def _target_names(targets) -> Set[str]:
    """Extract simple variable names from assignment targets."""
    names: Set[str] = set()
    for t in targets:
        if isinstance(t, ast.Name):
            names.add(t.id)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for elt in t.elts:
                if isinstance(elt, ast.Name):
                    names.add(elt.id)
    return names

def _call_name(call: ast.Call) -> str:
    """Best-effort function name for a call (handles Name/Attribute)."""
    try:
        return ast.unparse(call.func)
    except Exception:
        if isinstance(call.func, ast.Name):
            return call.func.id
        return ""


# #####################################################################################################################


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "stores":
        return do_stores(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "returns":
        return do_returns(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "taints":
        return do_taints(sys.argv[2])
    else:
        print("Usage: python cfgbugs.py <cmd> <file>")
        return -1
    
# Exercise 1
def do_stores(fname):
    print("STORES not implemented")
    return -1

# Exercise 2
def do_returns(fname):
    tree = open_file(fname)
    cfg = make_cfg_for_function(tree)
    mark_blocks_reaching_exit_without_return(cfg)




# Exercise 3
def do_taints(fname):
    tree = open_file(fname)
    cfg = make_cfg_for_function(tree)

    preds = {bb: [] for bb in cfg.blocks}
    for src, dst in cfg.edges:
        preds[dst].append(src)

    IN  = {bb: set() for bb in cfg.blocks}
    OUT = {bb: set() for bb in cfg.blocks}

    # Worklist = all blocks (forward analysis)
    from collections import deque
    wl = deque(cfg.blocks)

    def transfer(bb, in_set: Set[str]) -> Set[str]:
        node = getattr(bb, "node", None)
        out = set(in_set)

        if isinstance(node, (ast.If, ast.While)):
            return out

        if isinstance(node, ast.Return):
            return out

        if isinstance(node, ast.Assign):
            targets = _target_names(node.targets)
            if isinstance(node.value, ast.Call) and _call_name(node.value) == "source":
                return out | targets

            if isinstance(node.value, (ast.Constant, ast.Constant)):
                return out - targets

            used_vars = _collect_vars(node.value)
            if used_vars & in_set:
                return out | targets
            else:
                return out - targets

        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            return out

        return out

    while wl:
        bb = wl.popleft()
        new_in = set().union(*(OUT[p] for p in preds[bb])) if preds[bb] else set()
        if new_in != IN[bb]:
            IN[bb] = new_in
            new_out = transfer(bb, IN[bb])
            if new_out != OUT[bb]:
                OUT[bb] = new_out
                for succ in bb.successors:
                    if succ not in wl:
                        wl.append(succ)
        else:
            new_out = transfer(bb, IN[bb])
            if new_out != OUT[bb]:
                OUT[bb] = new_out
                for succ in bb.successors:
                    if succ not in wl:
                        wl.append(succ)

    for bb in cfg.blocks:
        node = getattr(bb, "node", None)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if _call_name(node.value) == "sink" and node.value.args:
                arg = node.value.args[0]
                used = _collect_vars(arg)
                tainted_here = sorted(v for v in used if v in IN[bb])
                for v in tainted_here:
                    print(f"BB{bb.id}: tainted variable {v} reaches sink")

    return 0



if __name__ == "__main__":
    main()
