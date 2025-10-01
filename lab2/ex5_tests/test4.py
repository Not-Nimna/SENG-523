import os

def myfunction(a, b):
    cmd1 = input()
    os.system(cmd1)  # first unsafe flow

    cmd2 = input()
    full = "ls " + cmd2
    os.system(full)  # second unsafe flow
