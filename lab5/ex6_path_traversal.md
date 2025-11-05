# Exercise 6 – Path Traversal (open / os.path.join)

## Goal
Warn on potential path traversal when `open()` or `os.path.join()` receive **variables** or **variable+constant mixes**; ignore calls with only **constant literals**.

## Rule idea (what my YAML does)
- Positive match via `pattern-either`:
  - `open($X)` (any dynamic expression).
  - `os.path.join($X, ...)` (dynamic components in joins).
- Exclude purely constant forms:
  - `open("...")`
  - `os.path.join("...", "...")`

## Effect on the sample
- **Flagged:** `opener_concat` (line 8), `opener_join_var` (line 16), `opener_join_varconst` (line 20).
- **Not flagged:** constant-only paths (e.g., lines 12, 24).

## Rationale
Unsanitized variables in paths can introduce `../` and escape intended directories. The rule highlights those risky constructions without warning on safe constants.

## Notes
This is a syntactic check (no taint tracking). Even if input is sanitized earlier, the rule will warn—acceptable for conservative security scanning.
