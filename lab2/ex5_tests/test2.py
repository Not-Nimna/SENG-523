import os
def myfunction(a, b):
    user_input = input()
    safe = "ls "
    full_cmd = safe + user_input
    os.system(full_cmd)
