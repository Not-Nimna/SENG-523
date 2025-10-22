import ast
import sys
from typing import List, Set, Optional, Tuple


_basic_block_counter = 0
def _next_basic_block_id_num() -> int:
    global _basic_block_counter
    _basic_block_counter += 1
    return _basic_block_counter

def _bb_label(n: int) -> str:
    return f"BB{n}"

def _collect_used_vars(node: Optional[ast.AST]) -> Set[str]:
    if node is None:
        return set()
    used = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            used.add(sub.id)
    return used

def _collect_defined_vars_from_target(target: ast.AST) -> Set[str]:
    defs = set()

    for sub in ast.walk(target):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
            defs.add(sub.id)
    return defs

class StatementType:
    ASSIGNMENT = "Assignment"
    IF = "If"
    WHILE = "While"
    PRINT = "Print"
    RETURN = "Return"
    OTHER = "Other"

class Statement:
    def __init__(self, stmt_type: str, def_set: Set[str], use_set: Set[str], ast_node: ast.AST):
        self.stmt_type = stmt_type
        self.def_set = def_set
        self.use_set = use_set
        self.ast_node = ast_node

class BasicBlock:
    def __init__(self, numeric_id: int, is_entry=False, is_exit=False):
        self.numeric_id = numeric_id              
        self.id = _bb_label(numeric_id)           
        self.is_entry = is_entry
        self.is_exit = is_exit
        self.statements: List[Statement] = []
        self.def_set: Set[str] = set()
        self.use_set: Set[str] = set()
        self.predecessors: Set["BasicBlock"] = set()
        self.successors: Set["BasicBlock"] = set()

    def add_statement(self, stmt: Statement):
        self.statements.append(stmt)
        self.def_set.update(stmt.def_set)
        self.use_set.update(stmt.use_set)

class EntryBlock(BasicBlock):
    def __init__(self):
        super().__init__()
        self.id = "Entry"

class ExitBlock(BasicBlock):
    def __init__(self):
        super().__init__()
        self.id = "Exit"

class ControlFlowGraph:
    def __init__(self):
        self.entry = BasicBlock(0, is_entry=True)
        self.exit: Optional[BasicBlock] = None
        self.blocks: Set[BasicBlock] = {self.entry}

    def new_block(self) -> BasicBlock:
        n = _next_basic_block_id_num()
        bb = BasicBlock(n)
        self.blocks.add(bb)
        return bb

    def ensure_exit(self) -> BasicBlock:
        if self.exit is None:
            n = _next_basic_block_id_num()
            self.exit = BasicBlock(n, is_exit=True)
            self.blocks.add(self.exit)
        return self.exit

    def add_edge(self, a: BasicBlock, b: BasicBlock):
        a.successors.add(b)
        b.predecessors.add(a)

    def print_cfg(self):
        # sort so it prints on order of bbs
        ordered = sorted(self.blocks, key=lambda b: b.numeric_id)
        for bb in ordered:
            if bb.is_entry:
                print(f"Basic Block {bb.id}: Entry")
                print("\tPredecessors:")
                succ_ids = ",".join(sorted([s.id for s in bb.successors], key=_bb_sort_key))
                print(f"\tSuccessors: {succ_ids}")
            elif bb.is_exit:
                print(f"Basic Block {bb.id}: Exit")
                pred_ids = ",".join(sorted([p.id for p in bb.predecessors], key=_bb_sort_key))
                print(f"\tPredecessors: {pred_ids}")
                print("\tSuccessors:")  # Exit has none
            else:
                print(f"Basic Block {bb.id}:")
                print("\tStatements:")
                for st in bb.statements:
                    defs_s = ",".join(sorted(st.def_set))
                    uses_s = ",".join(sorted(st.use_set))
                    print(f"\t{st.stmt_type}: defs: {defs_s}; uses: {uses_s}")
                pred_ids = ",".join(sorted([p.id for p in bb.predecessors], key=_bb_sort_key))
                succ_ids = ",".join(sorted([s.id for s in bb.successors], key=_bb_sort_key))
                print(f"\tPredecessors: {pred_ids}")
                print(f"\tSuccessors: {succ_ids}")

def _bb_sort_key(bb_id: str) -> Tuple[int, int]:
    if bb_id.startswith("BB"):
        try:
            return (0, int(bb_id[2:]))
        except ValueError:
            return (1, 0)
    return (1, 0)

def build_from_stmt_list(cfg: ControlFlowGraph, stmts: List[ast.stmt], incoming: BasicBlock) -> Optional[BasicBlock]:
    current = incoming
    for s in stmts:
        if isinstance(s, ast.Assign):

            defs = set()
            for t in s.targets:
                defs |= _collect_defined_vars_from_target(t)
            uses = _collect_used_vars(s.value)
            current.add_statement(Statement(StatementType.ASSIGNMENT, defs, uses, s))

        elif isinstance(s, ast.Expr):

            if isinstance(s.value, ast.Call) and isinstance(s.value.func, ast.Name) and s.value.func.id == "print":
                uses = set()
                for arg in s.value.args:
                    uses |= _collect_used_vars(arg)
                current.add_statement(Statement(StatementType.PRINT, set(), uses, s))
            else:

                uses = _collect_used_vars(s.value)
                current.add_statement(Statement(StatementType.OTHER, set(), uses, s))

        elif isinstance(s, ast.Return):
            uses = _collect_used_vars(s.value)
            current.add_statement(Statement(StatementType.RETURN, set(), uses, s))

            exit_bb = cfg.ensure_exit()
            cfg.add_edge(current, exit_bb)
            return None  #
        
        elif isinstance(s, ast.If):
            cond_uses = _collect_used_vars(s.test)
            current.add_statement(Statement(StatementType.IF, set(), cond_uses, s))
            then_head = cfg.new_block()
            cfg.add_edge(current, then_head)
            then_tail = build_from_stmt_list(cfg, s.body, then_head)
            if then_tail is None:
                pass

            if s.orelse:
                else_head = cfg.new_block()
                cfg.add_edge(current, else_head)
                else_tail = build_from_stmt_list(cfg, s.orelse, else_head)
            else:
                else_head = cfg.new_block()
                cfg.add_edge(current, else_head)
                else_tail = else_head  

            join_block = cfg.new_block()
            if then_tail is not None:
                cfg.add_edge(then_tail, join_block)
            if else_tail is not None:
                cfg.add_edge(else_tail, join_block)

            current = join_block  
            
        elif isinstance(s, ast.While):

            cond_block = cfg.new_block()
            cfg.add_edge(current, cond_block)


            cond_uses = _collect_used_vars(s.test)
            cond_block.add_statement(Statement(StatementType.WHILE, set(), cond_uses, s))


            body_head = cfg.new_block()
            cfg.add_edge(cond_block, body_head)
            body_tail = build_from_stmt_list(cfg, s.body, body_head)
            if body_tail is None:

                pass
            else:

                cfg.add_edge(body_tail, cond_block)

            after_loop = cfg.new_block()
            cfg.add_edge(cond_block, after_loop)
            current = after_loop

        else:
            uses = set()
            for sub in ast.walk(s):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                    uses.add(sub.id)
            current.add_statement(Statement(StatementType.OTHER, set(), uses, s))

    return current

def _fmt_defs(defs: set) -> str:
    return ", ".join(sorted(f"({v}, {b})" for (v, b) in defs))

def make_cfg(ast_node: ast.AST) -> ControlFlowGraph:
    cfg = ControlFlowGraph()

    start = cfg.new_block()
    cfg.add_edge(cfg.entry, start)
    tail = build_from_stmt_list(cfg, getattr(ast_node, "body", []), start)


    exit_bb = cfg.ensure_exit()
    if tail is not None:
        cfg.add_edge(tail, exit_bb)
    return cfg

def open_file(fname: str) -> ast.AST:
    with open(fname, "r") as f:
        src = f.read()
    return ast.parse(src, filename=fname)

def do_CFG(fname: str):
    tree = open_file(fname)
    cfg = make_cfg(tree)
    cfg.print_cfg()
    return 0

def do_liveness(fname):
    with open(fname, "r") as f:
        source = f.read()
    tree = ast.parse(source)
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

def do_reaching(fname):
    tree = open_file(fname)
    cfg = make_cfg(tree)

    all_defs = {(v, bb.id) for bb in cfg.blocks for v in bb.def_set}

    gen, kill = {}, {}
    for bb in cfg.blocks:
        gen[bb]  = {(v, bb.id) for v in bb.def_set}
        kill[bb] = {(v, other) for (v, other) in all_defs
                               if v in bb.def_set and other != bb.id}

    in_sets  = {bb: set() for bb in cfg.blocks}
    out_sets = {bb: set() for bb in cfg.blocks}

    changed = True
    while changed:
        changed = False
        for bb in sorted(cfg.blocks, key=lambda b: b.numeric_id):
            if bb.is_entry:
                continue
            new_in = set().union(*(out_sets[p] for p in bb.predecessors))
            new_out = gen[bb] | (new_in - kill[bb])
            if new_in != in_sets[bb] or new_out != out_sets[bb]:
                in_sets[bb], out_sets[bb] = new_in, new_out
                changed = True

    # print da results
    ordered = sorted(cfg.blocks, key=lambda b: b.numeric_id)
    for bb in ordered:
        print(f"Basic Block {bb.id}:")
        if bb.is_entry:
            print("\tPredecessors:")
            print("\tSuccessors: " + ",".join(s.id for s in bb.successors))
            continue
        if bb.is_exit:
            preds = ",".join(p.id for p in bb.predecessors)
            print(f"\tPredecessors: {preds}")
            print("\tSuccessors:")
            continue

        print(f"\tgens: {_fmt_defs(gen[bb])}")
        print(f"\tkills: {_fmt_defs(kill[bb])}")
        print(f"\tin: {_fmt_defs(in_sets[bb])}")
        print(f"\tout: {_fmt_defs(out_sets[bb])}")
        preds = ",".join(p.id for p in bb.predecessors)
        succs = ",".join(s.id for s in bb.successors)
        print(f"\tPredecessors: {preds}")
        print(f"\tSuccessors: {succs}")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "CFG":
        sys.exit(do_CFG(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "liveness":
        sys.exit(do_liveness(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "reaching":
        sys.exit(do_reaching(sys.argv[2]))
    else:
        print("Usage: python cfg.py <CFG|liveness|reaching> <file>")
        sys.exit(-1)

if __name__ == "__main__":
    main()
