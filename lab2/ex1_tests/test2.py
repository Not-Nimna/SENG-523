def outiefunc (a, b):
    c = 30 # <--c is defined, but not used
    d = a + b
    def inniefunc(x, y):
        c = 15 # <--this is a different c!
        return c
    return d