import os

def myfunction(a, b):
    cmd = input()
    cmd2 = "ls –l " + cmd
    cmd3 = sanitized(cmd2)
    os.system(cmd3)