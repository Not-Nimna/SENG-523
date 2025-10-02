import os
def myfunction(a, b):
    cmd = input()
    cmd2 = "ls -l " + cmd
    cmd3 = remove_spaces(cmd2)
    os.system(cmd3)