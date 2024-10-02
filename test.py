import pickle 
import copy
class B:
    def __init__(self, parent):
        self.a = 123
        self.b = 1233121
        self.c = 'qweqweqewq'

    def bar(self, i):
        print(i+123)

class A:
    a = 123
    def __init__(self):
        self.a = 123
        self.b = 321
        self.c = [123123, (12, 32), 123123]
        self.d = (32131231, 123123)
        self.e = {'12312': 2313, 3213123: ['qweqwe', (12312,)], (123, 321): {123312: 321, 543543: 0}}
        self.f = B(self)

var = A()

with open('test.pkl', 'wb') as file:
    pickle.dump(var, file, protocol=5)

with open('test.pkl', 'rb') as file:
    var1 = pickle.load(file)

print(var.__dict__)
print(var.f.__dict__)
var.f.bar(321)
print(var1.__dict__)
print(var1.f.__dict__)
var1.f.bar(123)

var2 = A()
print(globals())
print(hex(id(var2)))
for key in var1.__dict__:
    var2.__dict__[key] = copy.deepcopy(var1.__dict__[key])

print(hex(id(var2)))
print(var2.__dict__)
print(var2.f.__dict__)
var2.f.bar(333)
# for key in tuple(var.__dict__):
#     del var.__dict__[key]
# print(globals())
# print(var.a)
# var.f.bar(123)
# print(var.__dict__)
# print(var2.__dict__)