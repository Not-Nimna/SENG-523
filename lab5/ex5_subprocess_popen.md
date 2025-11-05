# Exercise 5 – subprocess with shell=True

## Goal
Warn when `subprocess.Popen(...)` or `subprocess.run(...)` are called with **`shell=True`** and a **variable/dynamic** command; ignore constant strings or fully literal argv lists.

## Rule idea (what my YAML does)
- Positive match: `subprocess.Popen($CMD, shell=True)` and `subprocess.run($CMD, shell=True)`.
- Exclusions:
  - Constant command strings: `"..."`.
  - Fully literal lists: `["...", "..."]`.

## Effect on the sample
- **Flagged:** `Popen("echo " + user, shell=True)` (line 8), `run(["sh","-c","echo " + user], shell=True)` (line 14).
- **Not flagged:** `popen1` (no shell), `popen3` (argv list, no shell), `popen5` (constant string + shell), `popen6` (constant list + shell).

## Rationale
`shell=True` lets the shell interpret metacharacters, so variable input is dangerous. Excluding constants and literal lists keeps the rule precise.

## Notes
If literal lists can still contain variables, ensure exclusions only suppress **fully** literal lists (the YAML is written that way).
