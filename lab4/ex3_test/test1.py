def func(x):
    x = source()
    y = x*2
    y = 3
    y = x
    x -= 1
    sink(y)


# BB3: tainted variable y reaches sink