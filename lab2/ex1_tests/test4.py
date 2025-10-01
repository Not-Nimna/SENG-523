def myfunction(a, b):
    x = 20 # <-- outer x
    def myotherfunction():
        x = 10 # <-- inner x aliases outer x