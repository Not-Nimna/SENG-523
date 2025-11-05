# Exercise 6 – Path Traversal (open / os.path.join)

## Goal
The goal is to only warn when `open()` or `os.path.join()` and use dynamic (variable) path parts or a mix of variables and constants. It shouldnt warn when the path is built from hard-coded strings only.

## How the rule works
- It matches to`open(x)` where `x` is any expression (variable, concat, f-string, join, etc.). or also to `os.path.join($X, ...)` where at least one component can be dynamic.
- It ignores purely constant calls like `open(".....")` and `os.path.join(".....", "...")`


## Effect on the sample
- **Flagged:** `opener_concat` (line 8), `opener_join_var` (line 16), `opener_join_varconst` (line 20).
- **Not flagged:** constant-only paths (e.g., lines 12, 24).

## Rationale
If user input ends up in a file path attackers can try `../` or similar tricks to escape the intended directory. By skipping the constant paths, the rule cuts nover oise and focuses on real traversal risks where variables are involved.






