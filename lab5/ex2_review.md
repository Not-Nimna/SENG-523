### 2.1 "command_injection.py"

theres basically a unsanitized variable being run in an os system call (on line 7)
there is also the same vulnerability on line 10 and 13 where a user can use command injection to run malicous code on the execution of the porogram.

### 2.2 "eval_exec.py"

here too there is unsanitized input goign into the eval fuction on line 2 and 5 but not on line 8 as thats a constat thats been fixed in place in the code

### 2.3 "path_traversal.py"

popen with the shell=True happens on lines 7, 13, 16 and 19 since this invokes the shell the uder can use command injection like how its being done on OS system calls
however, of those commans only lines 7 (popen2) and 13 (popen4) are vulnerabiliteis as the lines 16 (popen5) and 19 (popen6) are constant variables that the user does not get to decide.

### 2.3 "path_traversal.py"

opener_concat on line 8, opener_join_var on line 16 and opener_join_varconst on line 20 both have path traversal vulnerabilities due to the unsaintezed use of the variables name and base beig used in the open() function
