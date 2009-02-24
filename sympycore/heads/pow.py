
__all__ = ['POW']

from .base import BinaryHead, heads_precedence, Head, Expr, Pair, ArithmeticHead

from ..core import init_module
init_module.import_heads()
init_module.import_lowlevel_operations()
init_module.import_numbers()

@init_module
def _init(module):
    from ..arithmetic.numbers import try_power
    module.try_power = try_power

class PowHead(ArithmeticHead):
    """ PowHead represents exponentiation operation, data is a 2-tuple
    of base and exponent expressions. Both can be number instances or
    algebra instances.
    """
    op_mth = '__pow__'
    op_rmth = '__rpow__'

    def is_data_ok(self, cls, data):
        if type(data) is tuple and len(data)==2:
            base, exp = data
            if isinstance(base, cls):
                if isinstance(exp, numbertypes):
                    return
                if isinstance(exp, cls):
                    if exp.head is NUMBER:
                        if isinstance(exp.data, numbertypes):
                            return
                        else:
                            return 'data[1] must be lowlevel number but got %s' % (type(exp.data))
                    else:
                        return
                else:
                    return 'data[1] must be %s instance but got %s' % ((cls, numbertypes), type(exp))
            else:
                return 'data[0] must be %s instance but got %s' % (cls, type(exp))
        else:
            return 'data must be 2-tuple'
        return

    def __repr__(self): return 'POW'

    def new(self, cls, (base, exp), evaluate=True):
        if exp==1:
            return base
        if exp==0 or base==1:
            return cls(NUMBER, 1)
        if not evaluate:
            return cls(self, (base, exp))
        if type(exp) is cls:
            h, d = exp.pair
            if h is NUMBER:
                exp = d
        if base.head is NUMBER and isinstance(exp, numbertypes):
            b = base.data
            if isinstance(b, numbertypes):
                r, base_exp_list = try_power(b, exp)
                if not base_exp_list:
                    return cls(NUMBER, r)
                if len(base_exp_list)==1:
                    b, e = base_exp_list[0]
                    rest = cls(POW, (cls(NUMBER, b), e))
                else:
                    d = {}
                    for b, e in base_exp_list:
                        d[cls(NUMBER, b)] = e
                    rest = cls(BASE_EXP_DICT, d)
                if r==1:
                    return rest
                return  cls(TERM_COEFF, (rest, r))
        return cls(self, (base, exp))

    def reevaluate(self, cls, (base, exp)):
        return base ** exp

    def data_to_str_and_precedence(self, cls, (base, exp)):
        pow_p = heads_precedence.POW
        div_p = heads_precedence.DIV
        if isinstance(base, Expr):
            b, b_p = base.head.data_to_str_and_precedence(cls, base.data)
        elif isinstance(base, numbertypes):
            b, b_p = NUMBER.data_to_str_and_precedence(cls, base)
        else:
            b, b_p = SYMBOL.data_to_str_and_precedence(cls, base)

        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, numbertypes):
                exp = d
        if isinstance(exp, numbertypes):
            if exp==0:
                return '1', heads_precedence.NUMBER
            if exp==1:
                return b, b_p
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
            if isinstance(exp, Expr):
                e, e_p = exp.head.data_to_str_and_precedence(cls, exp.data)
            else:
                e, e_p = str(exp), 0.0
        s1 = '('+b+')' if b_p <= pow_p else b
        s2 = '('+e+')' if e_p < pow_p else e
        return s1 + '**' + s2, pow_p

    def to_EXP_COEFF_DICT(self, cls, (base, exp), expr, variables=None):
        if isinstance(exp, Expr):
            if exp.head is NUMBER:
                exp = exp.data
            elif exp.head is TERM_COEFF:
                t. c = exp.data
                return self.to_EXP_COEFF_DICT(cls, (base**t, c), expr, variables)
        if isinstance(exp, inttypes):
            return base.head.to_EXP_COEFF_DICT(cls, base.data, base, variables) ** exp
        if isinstance(exp, rationaltypes):
            numer, denom = exp
            if numer!=1:
                return self.to_EXP_COEFF_DICT(cls, (base**(exp/numer), numer), expr, variables)
        raise NotImplementedError(`base, exp`)

    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(TERM_COEFF, (expr, -1))

    def add(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is SYMBOL:
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        if rhead is NUMBER:
            if rdata==0:
                return lhs
            return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):rdata})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            if term==lhs:
                return term_coeff_new(cls, (term, coeff + 1))
            return cls(TERM_COEFF_DICT, {lhs:1, term:coeff})
        if rhead is TERM_COEFF_DICT:
            data = rdata.copy()
            dict_add_item(cls, data, lhs, 1)
            return term_coeff_dict_new(cls, data)
        if rhead is POW:
            if lhs==rhs:
                return cls(TERM_COEFF, (lhs, 2))
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        if rhead is BASE_EXP_DICT:
            assert not (len(rdata)==2 and 1 in rdata),'todo: handle the case x**2 + 3*x**2'
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        raise NotImplementedError(`self, rhs.head`)

    inplace_add = add

    def add_number(self, cls, lhs, rhs):
        if rhs==0:
            return lhs
        return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):rhs})

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def non_commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return term_coeff_new(cls, (lhs, rdata))
        if rhead is SYMBOL or rhead is POW:
            return MUL.combine(cls, [lhs, rhs])
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def commutative_mul_number(self, cls, lhs, rhs):
        if rhs==1:
            return lhs
        if rhs==0:
            return cls(NUMBER, 0)
        return cls(TERM_COEFF, (lhs, rhs))

    non_commutative_mul_number = commutative_mul_number

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return term_coeff_new(cls, (lhs, rdata))
        if rhead is SYMBOL or rhead is ADD or rhead is TERM_COEFF_DICT or rhead is APPLY:
            lbase, lexp = lhs.data
            if lbase == rhs:
                return pow_new(cls, (lbase, lexp + 1))
            return cls(BASE_EXP_DICT, {rhs:1, lbase:lexp})
        if rhead is POW:
            lbase, lexp = lhs.data
            rbase, rexp = rdata
            if lbase==rbase:
                return POW.new(cls, (lbase, lexp + rexp))
            return cls(BASE_EXP_DICT, {lbase:lexp, rbase:rexp})
        if rhead is BASE_EXP_DICT:
            base, exp = lhs.data
            data = rhs.data.copy()
            dict_add_item(cls, data, base, exp)
            return base_exp_dict_new(cls, data)
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr:1})

    def base_exp(self, cls, expr):
        base, exp = expr.data
        return base, exp

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if isinstance(exp, Expr) and exp.head is NUMBER:
            exp = exp.data
        if isinstance(exp, inttypes):
            b, e = base.data
            base, exp = b, e*exp
        
        return POW.new(cls, (base, exp))

    pow_number = pow

    def walk(self, func, cls, data, target):
        base, exp = data
        base1 = base.head.walk(func, cls, base.data, base)
        if isinstance(exp, Expr):
            exp1 = exp.head.walk(func, cls, exp.data, exp)
        else:
            exp1 = NUMBER.walk(func, cls, exp, exp)
        if base1 is base and exp1 is exp:
            return func(cls, self, data, target)
        else:
            r = base1 ** exp1
            return func(cls, r.head, r.data, r)

    def scan(self, proc, cls, data, target):
        base, exp = data
        base.head.scan(proc, cls, base.data, target)
        if isinstance(exp, Expr):
            exp.head.scan(proc, cls, exp.data, target)
        else:
            NUMBER.scan(proc, cls, exp, target)
        proc(cls, self, data, target)

    def expand(self, cls, expr):
        base, exp = expr.data
        if isinstance(exp, Expr):
            exp = exp.expand()
            h, d = exp.pair
            if h is NUMBER and isinstance(d, int):
                exp = d
        if isinstance(base, Expr):
            base = base.expand()
            if isinstance(exp, int):
                return base.head.expand_intpow(cls, base, exp)
        return cls(POW, (base, exp))

POW = PowHead()
