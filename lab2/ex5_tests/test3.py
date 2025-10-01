import os
def myfunction(a, b):
    if a > 0:
        cmd = input()
    else:
        cmd = "echo safe"
    os.system(cmd)
