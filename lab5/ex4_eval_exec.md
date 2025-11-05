# Exercise 4 – eval / exec with variable input

## Goal
Warn only when `eval()` or `exec()` are given dynamic (variable) input**. Do not warn when they’re called with a hard-coded string.


## How does this work?
- It matches both `eval(X)` and `exec(X)` (where `X` could be a variable, concat, f-string, etc.).
- It  will skip calls like `eval("...")` or `exec("...")` if they are using a plain string literal.

## Effect on the sample
- **Flagged:** `eval(expr)` (line 2) and `exec(code)` (line 5) — arguments are variables.
- **Not flagged:** `eval("1 + 2")` (line 8) — constant literal.

## Rationale
`eval` and `exec` run whatever code you hand them. The real danger is when untrusted input gets evaluated . Ignoring constant strings can keep the noise down and as a result we can focus on the actual risky cases.


