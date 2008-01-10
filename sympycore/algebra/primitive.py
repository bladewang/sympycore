
from __future__ import absolute_import
import types
import re
import compiler
from compiler import ast

from .algebraic_structures import BasicAlgebra

OR = intern(' or ')
AND = intern(' and ')
NOT = intern('not ')

LT = intern('<')
LE = intern('<=')
GT = intern('>')
GE = intern('>=')
EQ = intern('==')
NE = intern('!=')

BAND = intern('&')
BOR = intern('|')
BXOR = intern('^')
INVERT = intern('~')

POS = intern('+')
NEG = intern('-')
ADD = intern(' + ')
SUB = intern(' - ')
MOD = intern('%')
MUL = intern('*')
DIV = intern('/')
POW = intern('**')

NUMBER = intern('N')
SYMBOL = intern('S')
APPLY = intern('A')
TUPLE = intern('T')
LAMBDA = intern('L')

# XXX: Unimplemented expression parts:
# XXX: LeftShift, RightShift, List*, Subscript, Slice, KeyWord, GetAttr, Ellipsis
# XXX: function calls assume no optional nor *args nor *kwargs, same applies to lambda

boolean_lst = [AND, OR, NOT]
compare_lst = [LT, LE, GT, GE, EQ, NE]
bit_lst = [BAND, BOR, BXOR, INVERT]
arith_lst = [POS, NEG, ADD, SUB, MOD, MUL, DIV, POW]
parentheses_map = {
    OR: [LAMBDA],
    AND: [LAMBDA, OR],
    NOT: [LAMBDA, AND, OR],
    LT: [LAMBDA] + boolean_lst,
    LE: [LAMBDA] + boolean_lst,
    GT: [LAMBDA] + boolean_lst,
    GE: [LAMBDA] + boolean_lst,
    EQ: [LAMBDA] + boolean_lst,
    NE: [LAMBDA] + boolean_lst,
    BOR: [LAMBDA] + compare_lst + boolean_lst,
    BXOR: [LAMBDA, BOR] + compare_lst + boolean_lst,
    BAND: [LAMBDA, BOR, BXOR] + compare_lst + boolean_lst,
    INVERT: [LAMBDA, BOR, BXOR, BAND] + compare_lst + boolean_lst,
    ADD: [LAMBDA] + compare_lst + boolean_lst,
    SUB: [LAMBDA, ADD] + compare_lst + boolean_lst,
    POS: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    NEG: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    MOD: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    MUL: [LAMBDA, ADD, SUB, POS, NEG, MOD] + compare_lst + boolean_lst,
    DIV: [LAMBDA, ADD, SUB, POS, NEG, MOD, MUL,] + compare_lst + boolean_lst,
    POW: [LAMBDA, ADD, SUB, POS, NEG, MOD, MUL, DIV, POW] + compare_lst + boolean_lst,
    }

_is_name = re.compile(r'\A[a-zA-z_]\w*\Z').match

class PrimitiveAlgebra(BasicAlgebra):

    def __new__(cls, tree):
        if hasattr(tree, 'as_primitive'):
            tree = tree.as_primitive()
        if isinstance(tree, str): # XXX: unicode
            tree = string2PrimitiveAlgebra(tree)
        if isinstance(tree, cls):
            return tree
        if not isinstance(tree, tuple):
            tree = (SYMBOL, tree)
        obj = object.__new__(cls)
        obj.tree = tree
        return obj

    def __repr__(self):
        return str(self.tree)

    @staticmethod
    def convert(obj):
        return PrimitiveAlgebra(obj)

    def as_primitive(self):
        return self

    def as_algebra(self, cls, source=None):
        head, rest = self.tree
        if head is NUMBER:
            return cls(rest, kind=NUMBER)
        if head is SYMBOL:
            return cls(rest, kind=SYMBOL)
        if head is ADD:
            return cls.Add([r.as_algebra(cls) for r in rest])
        if head is SUB:
            return rest[0].as_algebra(cls) - cls.Add([r.as_algebra(cls) for r in rest[1:]])
        if head is MUL:
            return cls.Mul([r.as_algebra(cls) for r in rest])
        if head is DIV:
            return rest[0].as_algebra(cls) / cls.Mul([r.as_algebra(cls) for r in rest[1:]])
        if head is POW:
            return cls.Pow(*[r.as_algebra(cls) for r in rest])
        if head is NEG:
            return -(rest[0].as_algebra(cls))
        if head is POS:
            return +(rest[0].as_algebra(cls))
        raise NotImplementedError('as_algebra(%s): %s' % (cls, self))

    def __str__(self):
        head, rest = self.tree
        if head is NUMBER or head is SYMBOL:
            return str(rest)
        if head is APPLY:
            func = rest[0]
            args = rest[1:]
            s = str(func)
            if _is_name(s):
                return '%s(%s)' % (s, ', '.join(map(str,args)))
            return '(%s)(%s)' % (s, ', '.join(map(str,args)))
        if head is LAMBDA:
            args = rest[0]
            body = rest[1]
            return 'lambda %s: %s' % (str(args)[1:-1], body)
        if head is TUPLE:
            return '(%s)' % (', '.join(map(str,rest)))
        l = []
        for t in rest:
            h = t.tree[0]
            s = str(t)
            if h is NUMBER and  s.startswith('-'):
                h = ADD
            if h in parentheses_map.get(head, [h]):
                l.append('(%s)' % s)
            else:
                l.append(s)
        if len(l)==1:
            return head + l[0]
        return head.join(l)

    def __eq__(self, other):
        if type(other) is PrimitiveAlgebra:
            return self.tree == other.tree
        return self.tree == other

    def __hash__(self):
        return hash(self.tree)

    def __add__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((ADD, (self, other)))
    def __radd__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((ADD, (other, self)))
    def __sub__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((SUB, (self, other)))
    def __rsub__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((SUB, (other, self)))
    def __mul__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((MUL, (self, other)))
    def __rmul__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((MUL, (other, self)))
    def __div__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((DIV, (self, other)))
    def __rdiv__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((DIV, (other, self)))
    def __pow__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((POW, (self, other)))
    def __rpow__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((POW, (other, self)))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__


########### string to PrimitiveAlgebra parser ############

node_names = []
skip_names = ['Module','Stmt','Discard']
for n, cls in ast.__dict__.items():
    if n in skip_names:
        continue
    if isinstance(cls, (type,types.ClassType)) and issubclass(cls, ast.Node):
        node_names.append(n)

node_map = dict(Add='ADD', Mul='MUL', Sub='SUB', Div='DIV', FloorDiv='DIV',
                UnaryAdd='POS', UnarySub='NEG', Mod='MOD', Not='NOT',
                Or='OR', And='AND', Power='POW',
                Bitand='BAND',Bitor='BOR',Bitxor='BXOR',CallFunc='APPLY',
                Tuple='TUPLE',
                )
compare_map = {'<':LT, '>':GT, '<=':LT, '>=':GE,
               '==':EQ, '!=':NE}

class PrimitiveWalker:

    def __init__(self):
        self.stack = []

    # for composite instance:
    def start(self, head):
        self.stack.append([head, []])
    def append(self, obj):
        stack = self.stack
        if not stack:
            stack.append(obj)
        else:
            stack[-1][1].append(obj)
    def end(self):
        head, lst = self.stack.pop()
        if self.stack:
            last = self.stack[-1]
            if last[0]==head and head in [ADD, MUL]:
                # apply associativity:
                last[1].extend(lst)
                return
        self.append(PrimitiveAlgebra((head, tuple(lst))))
    # for atomic instance:
    def add(self, obj):
        self.append(PrimitiveAlgebra(obj))

    for _n in node_names:
        if _n in node_map:
            continue
        exec '''\
def visit%s(self, node, *args):
    print "warning: using default visit%s"
    self.start(%r)
    for child in node.getChildNodes():
        self.visit(child, *args)
    self.end()
''' % (_n, _n, _n)

    for _n,_v in node_map.items():
        exec '''\
def visit%s(self, node):
    self.start(%s)
    for child in node.getChildNodes():
        self.visit(child)
    self.end()
''' % (_n, _v)

    # visitNode methods:
    def visitName(self, node):
        self.add((SYMBOL, node.name))

    def visitConst(self, node):
        self.add((NUMBER, node.value))

    def visitCompare(self, node):
        lhs = node.expr
        op, rhs = node.ops[0]
        if len(node.ops)==1:
            self.start(compare_map[op])
            self.visit(lhs)
            self.visit(rhs)
            self.end()
            return
        n = ast.And([ast.Compare(lhs, node.ops[:1]),
                     ast.Compare(rhs, node.ops[1:])])
        self.visit(n)

    def visitLambda(self, node):
        self.start(LAMBDA)
        self.visit(ast.Tuple([ast.Name(n) for n in node.argnames]))
        self.visit(node.code)
        self.end()

def string2PrimitiveAlgebra(expr):
    """ Parse string expr to PrimitiveAlgebra.
    """
    node = compiler.parse(expr)
    return compiler.walk(node, PrimitiveWalker()).stack.pop()
