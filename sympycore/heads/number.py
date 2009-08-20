
__all__ = ['NUMBER']

import re

from .base import Head, Expr, heads_precedence, AtomicHead, Pair

from ..core import init_module
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

_is_number = re.compile(r'\A[-]?\d+\Z').match
_is_neg_number = re.compile(r'\A-\d+([/]\d+)?\Z').match
_is_rational = re.compile(r'\A\d+[/]\d+\Z').match

class NumberHead(AtomicHead):
    """
    NumberHead is a head for symbols, data can be any Python object.
    """

    def __repr__(self): return 'NUMBER'

    def new(self, cls, data):
        if isinstance(data, Infinity):
            return data
        return cls(NUMBER, data)

    def reevaluate(self, cls, data):
        return cls(self, data)

    def is_data_ok(self, cls, data):
        return

    def nonzero(self, cls, data):
        return data

    def to_SPARSE_POLY(self, cls, data, expr):
        """
        Obsolete method:  SPARSE_POLY will be removed in future.
        """
        return cls(data)
        
    def to_EXP_COEFF_DICT(self, cls, data, expr, variables = None):
        if variables is None:
            variables = ()
        return cls(EXP_COEFF_DICT, Pair(variables, {(0,)*len(variables):data}))

    def data_to_str_and_precedence(self, cls, data):
        if isinstance(data, complextypes):
            r, i = data.real, data.imag
            if r!=0 and i!=0:
                return str(data), heads_precedence.ADD
            if r==0:
                if i<0:
                    return str(data), heads_precedence.NEG
                return str(data), heads_precedence.NUMBER
            return self.data_to_str_and_precedence(self, cls, r)
        elif isinstance(data, rationaltypes):
            if data < 0:
                return str(data), heads_precedence.NEG
            return str(data), heads_precedence.DIV
        elif isinstance(data, realtypes):
            if data < 0:
                return str(data), heads_precedence.NEG
            return str(data), heads_precedence.NUMBER
        elif isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str_and_precedence(type(data), d)
        return str(data), 0.0 # force parenthesis

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            return cls(NUMBER, lhs.data * data)
        # Numbers are ring commutants:
        return rhs.head.non_commutative_mul(cls, rhs, lhs)

    def commutative_mul_number(self, cls, lhs, rhs):
        return cls(NUMBER, lhs.data * rhs)

    non_commutative_rmul_number = commutative_mul_number

    def commutative_div_number(self, cls, lhs, rhs):
        return cls(NUMBER, number_div(cls, lhs.data, rhs))

    def commutative_rdiv_number(self, cls, lhs, rhs):
        return cls(NUMBER, number_div(cls, rhs, lhs.data))

    def commutative_div(self, cls, lhs, rhs):
        return rhs.head.commutative_rdiv_number(cls, rhs, lhs.data)

    non_commutative_mul_number = commutative_mul_number

    def commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            return cls(NUMBER, lhs.data * data)
        return rhs.head.commutative_mul(cls, rhs, lhs)

    inplace_commutative_mul = commutative_mul

    def term_coeff(self, cls, expr):
        if isinstance(expr, Expr):
            return cls(NUMBER, 1), expr.data
        return cls(NUMBER, 1), expr

    def neg(self, cls, expr):
        return cls(self, -expr.data)

    def add(self, cls, lhs, rhs):
        ldata = lhs.data
        if ldata==0:
            return rhs
        h, d = rhs.pair
        if h is NUMBER:
            return cls(NUMBER, ldata + d)
        elif h is SYMBOL or h is APPLY or h is CALLABLE:
            return cls(TERM_COEFF_DICT, {cls(NUMBER,1): ldata, rhs:1})
        elif h is ADD:
            terms = []
            for term in d:
                h1, c = term.pair
                if h1 is NUMBER:
                    c = lhs.data + c
                    if c:
                        terms.append(cls(NUMBER, c))
                else:
                    terms.append(term)
            if not terms:
                return cls(NUMBER, 0)
            if len(terms)==1:
                return terms[0]
            return cls(ADD, terms)
        elif h is TERM_COEFF:
            term, coeff = d
            return cls(TERM_COEFF_DICT, {term:coeff, cls(NUMBER,1):lhs.data})
        elif h is POW or h is BASE_EXP_DICT:
            return cls(TERM_COEFF_DICT, {cls(NUMBER,1):lhs.data, rhs:1})
        elif h is TERM_COEFF_DICT:
            data = d.copy()
            dict_add_item(cls, data, cls(NUMBER,1), lhs.data)
            return term_coeff_dict_new(cls, data)
        raise NotImplementedError(`self, lhs.pair, rhs.pair`)

    inplace_add = add

    def add_number(self, cls, lhs, rhs):
        return cls(NUMBER, lhs.data + rhs) if rhs else lhs

    def sub_number(self, cls, lhs, rhs):
        return cls(NUMBER, lhs.data - rhs) if rhs else lhs

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def pow(self, cls, base, exp):
        h, d = exp.pair
        if h is NUMBER and type(d) in numbertypes_set:
            return self.pow_number(cls, base, d)
        return pow_new(cls, (base, exp))

    def pow_number(self, cls, base, exp):
        if exp==1:
            return base
        if exp==0:
            return cls(NUMBER, 1)
        bd = base.data
        if bd==1:
            return base
        r, l = try_power(bd, exp)
        if not l:
            return cls(NUMBER, r)
        if len(l)==1:
            b, e = l[0]
            if r==1:
                return cls(POW, (cls(NUMBER, b), e))
            return cls(TERM_COEFF, (cls(POW, (cls(NUMBER, b), e)), r))
        d = {}
        for b, e in l:
            d[cls(NUMBER, b)] = e
        if r == 1:
            return cls(BASE_EXP_DICT, d)
        return cls(TERM_COEFF, (cls(BASE_EXP_DICT, d), r))

    def expand(self, cls, expr):
        return expr

    def diff(self, cls, data, expr, symbol, order, cache={}):
        #if isinstance(data, Expr):
        #    return cls(NUMBER, data.head.diff(type(data), data.data, data, symbol, order))
        return cls(NUMBER, 0)

    def apply(self, cls, data, func, args):
        if isinstance(data, cls):
            return data
        return cls(NUMBER, data)

    def integrate_indefinite(self, cls, data, expr, x):
        if data==0:
            return expr
        if data==1:
            return cls(SYMBOL, x)
        return cls(TERM_COEFF, (cls(SYMBOL, x), data))

    def integrate_definite(self, cls, data, expr, x, a, b):
        if data==0:
            return expr
        if data==1:
            return b-a
        return (b-a)*data

NUMBER = NumberHead()
