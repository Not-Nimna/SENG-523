# Exercise 5 – subprocess with shell=True

## Goal
Warn only when `subprocess.Popen()` or `subprocess.run()` are called with `shell=True` and a variable or dynamic command; ignore constant strings or fully literal argv lists.

## How the rule works?
- It looks for when `subprocess.Popen(cmd, shell=True)` and `subprocess.run(cmd, shell=True)` (where `cmd` can be a variable, concat, f-string, etc.).
- It skips safe cases like if its constant strings like `"echo hello"`and any fully literal lists like `["echo", "hello"]`.

## Effect on the sample
- **Flagged:** `Popen("echo " + user, shell=True)` (line 8), `run(["sh","-c","echo " + user], shell=True)` (line 14).
- **Not flagged:** `popen1` (no shell), `popen3` (argv list, no shell), `popen5` (constant string + shell), `popen6` (constant list + shell).

## Rationale
When `shell=True` is set, the shell can interpret metacharacters (`;`, `&&`, `|`, `$()`), so *variable input is risky. Beacause we are ignoring constants and fully literal lists, the rule stays focused on real injection scenarios instead of noisy false positives.


