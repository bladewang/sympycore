
from ..core import Basic, BasicType
from ..core.utils import UniversalMethod
from .methods import ArithmeticMethods

class BasicArithmetic(ArithmeticMethods, Basic):
    """ Defines default methods for arithmetic classes.
    """
    def try_power(self, exponent):
        """ Try evaluating power self ** exponent.
        Return None if no evaluation is carried out.
        Caller code must ensure that exponent is
        a Basic instance.
        """
        return

    @UniversalMethod
    def fdiff(obj, index=1):
        assert not isinstance(obj, BasicType),`obj`
        return Basic.Number(0)

    def try_derivative(self, s):
        return None

    def expand(self, *args, **kwargs):
        return self

    def split(self, op, *args, **kwargs):
        if op == '**':
            return [self, Basic.Number(1)]
        return [self]

    def diff(self, *symbols):
        """ Return derivative with respect to symbols. If symbols contains
        positive integer then differentation is repeated as many times as
        is the value with respect to preceding symbol in symbols.
        """
        new_symbols = []
        for s in symbols:
            s = Basic.sympify(s)
            if s.is_Integer and new_symbols and s.is_positive:
                last_s = new_symbols.pop()
                new_symbols += [last_s] * int(s)
            elif s.is_Symbol:
                new_symbols.append(s)
            else:
                raise TypeError(".diff() argument must be Symbol|Integer instance (got %s)"\
                                % (s.__class__.__name__))
        expr = self
        unused_symbols = []
        for s in new_symbols:
            obj = expr.try_derivative(s)
            if obj is not None:
                expr = obj
            else:
                unused_symbols.append(s)
        if not unused_symbols:
            return expr
        for s in unused_symbols:
            if not expr.has(s):
                return Basic.zero
        return Basic.Derivative(self, *new_symbols)