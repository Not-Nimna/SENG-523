# Exercise 4 – eval / exec with variable input

## Goal
Warn only when `eval()` or `exec()` receive **variable/dynamic** input; ignore calls with **constant literals**.

## Rule idea (what my YAML does)
- Use `pattern-either` to match both: `eval($X)` and `exec($X)`.
- Suppress constant cases with `pattern-not-either` for `eval("...")` and `exec("...")`.

## Effect on the sample
- **Flagged:** `eval(expr)` (line 2) and `exec(code)` (line 5) — arguments are variables.
- **Not flagged:** `eval("1 + 2")` (line 8) — constant literal.

## Rationale
`eval`/`exec` execute strings as Python code. Restricting findings to variable input highlights true RCE risk while avoiding false positives on fixed test literals.

## Notes
If the project uses wrapper functions around `eval`/`exec`, complementary rules would be required to catch those paths.
