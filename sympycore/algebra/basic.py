
from ..core import Basic, classes, objects

class AlgebraicExpression(Basic):
    """ Algebraic expression represents

    - a set element of an algebra
    - a result of binary operation +
    - a result of binary operation *

    An operant of the operation + has number coefficient that
    represents a repetition of the given operant in the operation.
    E.g. x * 3 means x + x + x. Number coefficient can be also
    fraction, algebraic number, or any other concept generalizing
    repetition notion.

    An operant of the operation * has integer exponent that also
    represents a repetition of the given operant in the operation.
    E.g. x ** 3 means x * x * x. The exponent must be integer.

    An element of an algebra is represented as

      AlgebraicExpression(ELEMENT, obj)
      
    where obj can be any Python object that is hashable.

    A result of the operation + is represented as

      AlgebraicExpression(TERMS, pairs)

    where pairs is a sequence or iterator containing pairs

      (<AlgebraicExpression instance>, <number coefficient>).

    A result of the operation * is represented as

      AlgebraicExpression(FACTORS, pairs)

    where pairs is a sequence or iterator containing pairs

      (<AlgebraicExpression instance>, <integer exponent>).

    Algebra contains identity element zero with respect to + operation.

    Algebra contains identity element one with respect to * operation.

    A number element of an algebra is defined as

      one * <number>

    and is represented as

      AlgebraicExpression(TERMS, [(one, <number>)]).

    The zero element of an algebra is represented as

      one * 0.

    Similarly, the one element of an algebra is represented as

      one * 1.

    Fractional powers are represented as powers of a minimal root
    (that has exponent with a nominator equal to 1) where the root
    expression is considered as an element of an algebra. E.g.
    x**(2/3) is equal to (x**(1/3)) ** 2 and is represented as

      AlgebraicExpression(FACTORS,
                      [(AlgebraicExpression(ELEMENT, x**(1/3)), 2)])

    where y=x**(1/3) is a solution of x==y**3 with respect to y and is
    represented as

      Root(x, 3).

    Symbolic powers are considered as an element of an algebra.
    E.g x**y is represented as
    
      AlgebraicExpression(ELEMENT, x**y)

    where x**y is represented as Power(x, y).

    More examples:
     x**(2/3*y) is represented as

      AlgebraicExpression(FACTORS,
                         [(AlgebraicExpression(ELEMENT, Power(x,1/3*y)) , 2)] )

     x**(2/3*y + 4/5) is rewritten as (x**(1/3*y+2/5), 2)

    Python operations + and * use the following rules when the lhs
    operant is an instance of AlgebraicExpression:
    
      - if rhs has the same class as lhs then result will be computed within
        given algebra.

      - if rhs is a subclass of the lhs class then it is considered
        as a number element of the lhs algebra.

      - if rhs is a superclass of tje lhs class then the lhs is considered
        as a number element of the rhs algebra.

      - if rhs is not an AlgebraicExpression instance then it will be
        converted to one using rhs.as_ae(lhs.__class__).

    Examples:

      <Number>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS,[(one, <Number>)])

      <Symbol>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS,[(s, 1)])
        where s = AlgebraicExpression(ELEMENT, <Symbol>)

      <Power(2,5/3)>.as_ae(AlgebraicExpression) -> AlgebraicExpression(FACTORS,[(s, 5)])
        where s = AlgebraicExpression(ELEMENT, <Power(2,1/3)>)
    """

    def __new__(cls, kind, expr):
        obj = object.__new__(cls)
        
class AlgebraicNumberExpression(AlgebraicExpression):
    """ Represents algebraic numbers.

    Here elements of the algebra are minimal roots of numbers and
    numbers. E.g. 2**(2/3) is represented as

      AlgebraicNumberExpression(FACTORS,
        [(AlgebraicNumberExpression(ELEMENT, Root(2,3)), 2)])
    """