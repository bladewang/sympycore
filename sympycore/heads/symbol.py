
__all__ = ['SYMBOL']

import re

from .base import AtomicHead, heads_precedence, Expr, Pair

_is_atomic = re.compile(r'\A\w+\Z').match

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class SymbolHead(AtomicHead):
    """
    SymbolHead is a head for symbols, data can be any Python object.
    """

    def __repr__(self): return 'SYMBOL'

    def data_to_str_and_precedence(self, cls, data):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str_and_precedence(cls, d)
        s = str(data)
        if _is_atomic(s):
            return s, heads_precedence.SYMBOL
        return s, 0.0 # force parenthesis

    def get_precedence_for_data(self, data, # obsolete
                                _p = heads_precedence.SYMBOL):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.get_precedence_for_data(d)
        return _p

    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr:-1})

    def as_add(self, cls, expr):
        return cls(ADD, [expr])
    
    def add(self, cls, lhs, rhs):
        if lhs==rhs:
            return cls(TERM_COEFF_DICT, {lhs:2})
        h = rhs.head
        if h is SYMBOL or h is NUMBER:
            return cls(ADD, [lhs, rhs])
        lhs = self.as_add(cls, lhs)
        return lhs.head.add(cls, lhs, rhs)

    def sub(self, cls, lhs, rhs):
        if lhs==rhs:
            return cls(NUMBER, 0)
        h = rhs.head
        if h is SYMBOL or h is NUMBER:
            return cls(SUB, [lhs, rhs])
        raise NotImplementedError(`self, lhs, h, rhs`)

    def as_ncmul(self, cls, expr):
        return cls(NCMUL, Pair(1, [expr])) # todo: check expr commutativity

    def base_exp(self, cls, expr):
        return expr, 1

    def ncmul(self, cls, lhs, rhs):
        if lhs==rhs:
            return cls(POW, (lhs, 2))
        h = rhs.head
        if h is SYMBOL:
            return cls(NCMUL, (1, [lhs, rhs]))
        lhs = self.as_ncmul(cls, lhs)
        return lhs.head.ncmul(cls, lhs, rhs)


    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        return cls(POW, (base, exp))

SYMBOL = SymbolHead()
