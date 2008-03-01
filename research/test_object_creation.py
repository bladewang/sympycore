
import timeit

src = '''
class Pairs(object):
    def __new__(cls, data, head, new=object.__new__):
        obj = new(cls)
        obj.head = head
        obj.data = data
        return obj


class Primitive(object):
    def __new__(cls, data, head, new=object.__new__):
        obj = new(cls)
        obj.tree = (head, data)
        return obj

    @property
    def data(self):
        return self.tree[1]

class Tuple1(tuple):
    def __new__(cls, data, head, new = tuple.__new__):
        obj = new(cls, (head, data))
        return obj

    @property
    def data(self):
        return self[1]

class Tuple2(tuple):

    @property
    def data(self):
        return self[0]

pairs = Pairs((1,2),"+")
primitive = Primitive((1,2),"+")
tuple1 = Tuple1((1,2),"+")
tuple2 = Tuple2(((1,2),"+"))
'''

n = 1000000
base_time = min(timeit.Timer('foo()', 'def foo(): pass').repeat(number=n))


for timer in [
  timeit.Timer('Pairs((1,2),"+")', src),
  timeit.Timer('Primitive((1,2),"+")', src),
  timeit.Timer('Tuple1((1,2),"+")', src),
  timeit.Timer('Tuple2(((1,2),"+"))', src),
  timeit.Timer('pairs.data', src),
  timeit.Timer('primitive.data', src),
  timeit.Timer('primitive.tree[1]', src),
  timeit.Timer('tuple1.data', src),
  timeit.Timer('tuple1[1]', src),
  timeit.Timer('tuple2.data', src),
  timeit.Timer('tuple2[0]', src),
  ]:
    print '%s: %.2f stones'\
    % (timer.src.splitlines()[-3].strip(),
    min(timer.repeat(number=n))/base_time)
    
