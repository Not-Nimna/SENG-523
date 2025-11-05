# Exercise 3 – Command Injection (os.system)

## Goal
Warn only on `os.system()` calls that use **variable/dynamic** input. Ignore calls with **constant literals**.

## How does this work?
- It looks for any call like `os.system(x)` (where `x` can be a variable, an f-string, a concat, etc.).
- It ignores calls that pass a plain string literal: `os.system("...")`.

## Effect on the sample
- **Flagged:** `os.system(cmd)` (line 7), `os.system("ls " + user)` (line 10), `os.system(f"echo {user}")` (line 13).
- **Not flagged:** `os.system("echo hello")` (line 4).

## Rationale
Command injection occurs when untrusted input reaches the shell. Filtering out the constant strings will reduce noise and focus on the exploitable flows anywhare attackers can insert shell metacharacters (`;`, `&&`, `|`, `$()`).

