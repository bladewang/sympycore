"""
This module defines arithmetic operations and expand
function for s-expressions. The following functions are defined:
  add(lhs, rhs)
  mul(lhs, rhs)
  power(base, intexp)
  expand(expr)
  tostr(expr)
with s-expression arguments (except intexp that must be Python integer)
and return values. The following s-expressions are supported:
  (SYMBOLIC, <object>)
  (NUMBER, <number object>)
  (TERMS, frozenset([(<term1>, <coeff1>), ...])) where <coeffs> are numbers
  (FACTORS, frozenset([(<base1>, <exp1>), ...])) where <exps> are integers
where <object> must be an immutable object that supports __eq__ with other
similar objects, <number object> must support arithmetic operations with
Python integers, <terms> and <bases> must be s-expressions.

Efficency and easy translation to C code has been kept in mind while writting
the code below.
"""

__all__ = ['add', 'mul', 'power', 'expand', 'tostr']

from ..core import classes
from ..core.sexpr import NUMBER, SYMBOLIC, TERMS, FACTORS

# output functions:

def tostr(expr, apply_parenthesis = False):
    """ Return s-expr as a readable string.
    Terms and factors are sorted lexicographically.
    """
    s = expr[0]
    if s==TERMS:
        l = ['%s*%s' % (c, tostr(t)) for t,c in expr[1]]
        l.sort()
        r = ' + '.join(l)
    elif s==FACTORS:
        l = ['%s**%i' % (tostr(t, t[0]==TERMS), c) for t,c in expr[1]]
        l.sort()
        r = ' * '.join(l)
    else:
        r = str(expr[1])
    if apply_parenthesis:
        r = '(%s)' % (r)
    return r

# arithmetic functions:

zero = (NUMBER, 0)
one = (NUMBER, 1)

def add_inplace_dict_terms(d, rhs, p):
    for t,c in rhs[1]:
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c==0:
                # XXX: check that t does not contain oo or nan
                del d[t]
            else:
                d[t] = c 
    return

def add_inplace_dict_number(d, rhs, p):
    return add_inplace_dict_terms(d, (TERMS, [(one, rhs[1])]), p)

def add_inplace_dict_nonterms(d, rhs, p):
    return add_inplace_dict_terms(d, (TERMS, [(rhs, 1)]), p)

def mul_inplace_dict_factors(d, rhs, p):
    for t,c in rhs[1]:
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c==0:
                # XXX: check that t does not contain nan
                del d[t]
            else:
                d[t] = c
    return

def terms_dict_to_expr(d):
    if not d:
        return zero
    if len(d)==1:
        t, c = d.items()[0]
        if c==1:
            return t
    return (TERMS, frozenset(d.iteritems()))

def factors_dict_to_expr(d):
    if not d:
        return one
    if len(d)==1:
        t, c = d.items()[0]
        if c==1:
            return t
    return (FACTORS, frozenset(d.iteritems()))

def add_terms_terms(lhs, rhs):
    d = dict(lhs[1])
    add_inplace_dict_terms(d, rhs, 1) # XXX: optimize 1
    return terms_dict_to_expr(d)

def add_terms_number(lhs, rhs):
    # XXX: optimize
    return add_terms_terms(lhs, (TERMS, [(one, rhs[1])]))

def add_terms_nonterms(lhs, rhs):
    # XXX: optimize
    return add_terms_terms(lhs, (TERMS, ((rhs, 1),)))

def add_nonterms_nonterms(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (TERMS, frozenset([(lhs, 2)]))
    return (TERMS, frozenset([(lhs, 1), (rhs, 1)]))

def add_number_number(lhs, rhs):
    return (NUMBER, lhs[1] + rhs[1])

def add_nonterms_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, 1), (one, rhs[1])]))

def add(lhs, rhs):
    """ Add two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1==s2==NUMBER: #XXX: optimize
        return add_number_number(lhs, rhs)
    if s1==s2==TERMS:
        return add_terms_terms(lhs, rhs)
    if s1==TERMS:
        if s2==NUMBER:
            return add_terms_number(lhs, rhs)
        return add_terms_nonterms(lhs, rhs)
    if s2==TERMS:
        if s1==NUMBER:
            return add_terms_number(rhs, lhs)
        return add_terms_nonterms(rhs, lhs)
    if s1==NUMBER:
        return add_nonterms_number(rhs, lhs)
    if s2==NUMBER:
        return add_nonterms_number(lhs, rhs)
    return add_nonterms_nonterms(lhs, rhs)

def add_inplace_dict(d, rhs, p):
    """ Add s-expression multiplied with p to dictionary d.
    """
    s = rhs[0]
    if s==TERMS:
        add_inplace_dict_terms(d, rhs, p)
    elif s==NUMBER:
        add_inplace_dict_number(d, rhs, p)
    else:
        add_inplace_dict_nonterms(d, rhs, p)
    return

def mul_factors_factors(lhs, rhs):
    d = dict(lhs[1])
    mul_inplace_dict_factors(d, rhs, 1)
    return factors_dict_to_expr(d)

def mul_number_number(lhs, rhs):
    return (NUMBER, lhs[1] * rhs[1])

def mul_factors_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, rhs[1])]))

def mul_factors_nonfactors(lhs, rhs):
    return mul_factors_factors(lhs, (FACTORS, [(rhs, 1)]))

def mul_nonfactors_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, rhs[1])]))

def mul_nonfactors_nonfactors(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (FACTORS, frozenset([(lhs, 2)]))
    return (FACTORS, frozenset([(lhs, 1), (rhs, 1)]))

def mul_terms_terms(lhs, rhs):
    if not (len(lhs[1])==len(rhs[1])==1):
        return mul_nonfactors_nonfactors(lhs, rhs)
    t1,c1 = list(lhs[1])[0]
    t2,c2 = list(rhs[1])[0]
    return mul(mul(t1, t2),(NUMBER, c1*c2))

def mul_terms_number(lhs, rhs):
    d = dict()
    add_inplace_dict_terms(d, lhs, rhs[1])
    return terms_dict_to_expr(d)

def mul_terms_factors(lhs, rhs):
    if not (len(lhs[1])==1):
        return mul_factors_nonfactors(rhs, lhs)
    t,c = list(lhs[1])[0]
    return mul(mul(t,rhs), (NUMBER, c))

def mul_terms_nonfactors(lhs, rhs):
    if not (len(lhs[1])==1):
        return mul_nonfactors_nonfactors(rhs, lhs)
    t,c = list(lhs[1])[0]
    return mul(mul(t,rhs), (NUMBER, c))

def mul(lhs, rhs):
    """ Multiply two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1==FACTORS:
        if s2==FACTORS:
            return mul_factors_factors(lhs, rhs)
        elif s2==TERMS:
            return mul_terms_factors(rhs, lhs)
        elif s2==NUMBER:
            return mul_factors_number(lhs, rhs)
        return mul_factors_nonfactors(lhs, rhs)
    elif s1==TERMS:
        if s2==FACTORS:
            return mul_terms_factors(lhs, rhs)
        elif s2==TERMS:
            return mul_terms_terms(lhs, rhs)
        elif s2==NUMBER:
            return mul_terms_number(lhs, rhs)
        return mul_terms_nonfactors(lhs, rhs)
    elif s1==NUMBER:
        if s2==FACTORS:
            return mul_factors_number(rhs, lhs)
        elif s2==TERMS:
            return mul_terms_number(rhs, lhs)
        elif s2==NUMBER:
            return mul_number_number(lhs, rhs)
        return mul_nonfactors_number(rhs, lhs)
    else:
        if s2==FACTORS:
            return mul_factors_nonfactors(rhs, lhs)
        elif s2==TERMS:
            return mul_terms_nonfactors(rhs, lhs)
        elif s2==NUMBER:
            return mul_nonfactors_number(lhs, rhs)
    return mul_nonfactors_nonfactors(lhs, rhs)

def power(base, exp):
    """ Find a power of an s-expression over integer exponent.
    """
    assert isinstance(exp, int),`type(exp)`
    if exp==1:
        return base
    elif exp==0:
        return one
    s = base[0]
    if s==NUMBER:
        return (NUMBER, base[1] ** exp)
    if s==TERMS:
        if len(base[1])==1 and exp!=1:
            t,c = list(base[1])[0]
            return mul(power(t, exp), (NUMBER,c ** exp))
    if s==FACTORS:
        d = dict()
        mul_inplace_dict_factors(d, base, exp)
        return factors_dict_to_expr(d)
    return (FACTORS, frozenset([(base, exp)]))

def expand_mul_terms_terms(lhs, rhs):
    d = dict()
    for t1,c1 in lhs[1]:
        for t2,c2 in rhs[1]:
            add_inplace_dict(d, mul(t1,t2), c1*c2)
    return terms_dict_to_expr(d)

def expand_mul_terms_nonterms(lhs, rhs):
    d = dict()
    for t,c in lhs[1]:
        add_inplace_dict(d, mul(t, rhs), c)
    return terms_dict_to_expr(d)

def expand_mul(lhs, rhs):
    """ Multiply s-expressions with expand.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1==s2==TERMS:
        return expand_mul_terms_terms(lhs, rhs)
    if s1==TERMS:
        return expand_mul_terms_nonterms(lhs, rhs)
    if s2==TERMS:
        return expand_mul_terms_nonterms(rhs, lhs)
    return mul(lhs, rhs)

def expand_terms(expr):
    d = dict()
    for t,c in expr[1]:
        add_inplace_dict(d, expand(t), c)
    return terms_dict_to_expr(d)

def expand_factors(expr):
    r = None
    for t,c in expr[1]:
        e = expand_power(expand(t), c)
        if r is None:
            r = e
        else:
            r = expand_mul(r, e)
    return r

def expand_power(expr, p):
    if p==1:
        return expr
    elif p<0 or expr[0]!=TERMS:
        return power(expr, p)
    ## Consider polynomial
    ##   P(x) = sum_{i=0}^n p_i x^k
    ## and its m-th exponent
    ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
    ## The coefficients a(m,k) can be computed using the
    ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
    ## Seminumerical Algorithms, The art of Computer
    ## Programming v.2, Addison Wesley, Reading, 1981;]:
    ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
    ## where a(m,0) = p_0^m.
    Fraction = classes.Fraction
    m = int(p)
    tc = list(expr[1])
    n = len(tc)-1
    t0,c0 = tc[0]
    p0 = [mul(mul(t, power(t0,-1)),(NUMBER, c/c0)) for t,c in tc]
    r = dict()
    add_inplace_dict(r, power(t0,m), c0**m)
    l = [terms_dict_to_expr(r)]
    for k in xrange(1, m * n + 1):
        r1 = dict()
        for i in xrange(1, min(n+1,k+1)):
            nn = (m+1)*i-k
            if nn:
                add_inplace_dict(r1, expand_mul(l[k-i], p0[i]), Fraction(nn,k)) # XXX: optimize expand_mul, it should not be needed
        f = terms_dict_to_expr(r1)
        add_inplace_dict(r, f, 1)
        l.append(f)
    return terms_dict_to_expr(r)

def expand(expr):
    """ Expand s-expression.
    """
    s = expr[0]
    if s==TERMS:
        return expand_terms(expr)
    if s==FACTORS:
        return expand_factors(expr)
    return expr


