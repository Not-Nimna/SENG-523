def func(x):
    x = source()
    while x < 10:
        x = 2
    y = source()
    y -= x
    sink(y)

# BB6: tainted variable y reaches sink