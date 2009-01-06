
__all__ = ['POW']

from .base import BinaryHead, heads_precedence, Head, Expr, Pair

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class PowHead(BinaryHead):
    """ PowHead represents exponentiation operation, data is a 2-tuple
    of base and exponent expressions.
    """
    precedence = Head.precedence_map['POW'] # obsolete
    op_mth = '__pow__'
    op_rmth = '__rpow__'
    op_symbol = '**' #obsolete
    def __repr__(self): return 'POW'

    def data_to_str_and_precedence(self, cls, (base, exp)):
        pow_p = heads_precedence.POW
        div_p = heads_precedence.DIV
        if isinstance(base, Expr):
            b, b_p = base.head.data_to_str_and_precedence(cls, base.data)
        else:
            b, b_p = NUMBER.data_to_str_and_precedence(cls, base)

        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, numbertypes):
                exp = d

        if isinstance(exp, numbertypes):
            if exp < 0:
                if exp==-1:
                    s1 = '('+b+')' if b_p <= pow_p else b
                    return '1/' + s1, div_p
                e, e_p = NUMBER.data_to_str_and_precedence(cls, -exp)
                s1 = '('+b+')' if b_p < pow_p else b
                s2 = '('+e+')' if e_p < pow_p else e
                return '1/' + s1 + '**' + s2, div_p
            e, e_p = NUMBER.data_to_str_and_precedence(cls, exp)
        else:
            e, e_p = exp.head.data_to_str_and_precedence(cls, exp)
        s1 = '('+b+')' if b_p < pow_p else b
        s2 = '('+e+')' if e_p < pow_p else e
        return s1 + '**' + s2, pow_p

    def as_ncmul(self, cls, expr):
        return cls(NCMUL, Pair(1, [expr])) # todo: check expr commutativity

    def base_exp(self, cls, expr):
        base, exp = expr.data
        return base, exp

    def ncmul(self, cls, lhs, rhs):
        lhs = self.as_ncmul(cls, lhs)
        return lhs.head.ncmul(cls, lhs, rhs)

    def pow(self, cls, base, exp):
        
        raise NotImplementedError(`base, exp`)

POW = PowHead()
