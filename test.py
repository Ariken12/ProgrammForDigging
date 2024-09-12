def func():
    a = 0
    while a >= 0:
        a += 1
        yield a

gen = func()
for i in range(10):
    print(next(gen))

print(list(enumerate({'123': 123, 'ewq': "adsf", 123: 312, (123, 321): '321'}, 1)))