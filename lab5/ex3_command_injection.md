# Exercise 3 – Command Injection (os.system)

## Goal
Warn only on `os.system()` calls that use **variable/dynamic** input, and ignore calls with **constant literals**.

## Rule idea (what my YAML does)
- Match every `os.system($X)` call (where `$X` can be any expression).
- Exclude constant-only cases with `pattern-not: os.system("...")`.

## Effect on the sample
- **Flagged:** `os.system(cmd)` (line 7), `os.system("ls " + user)` (line 10), `os.system(f"echo {user}")` (line 13).
- **Not flagged:** `os.system("echo hello")` (line 4).

## Rationale
Command injection occurs when untrusted input reaches the shell. Filtering out constant strings reduces noise and focuses on exploitable flows where attackers can insert shell metacharacters (`;`, `&&`, `|`, `$()`).

## Notes
If a project wraps `os.system` in helper functions, additional rules would be needed to match those wrappers.
