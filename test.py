def func():
    a = 0
    while a >= 0:
        a += 1
        yield a

gen = func()
for i in range(10):
    print(next(gen))
