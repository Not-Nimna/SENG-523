def outiefunc (a, b):
    c = 30 # <-- c is defined here...
    d = a + b
    def inniefunc(x, y):
        retval = c*2 # <-- ...and used here
        return retval
    return d