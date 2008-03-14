
from ..core import classes
from ..utils import EQ, NE, LT, LE, GT, GE
from ..basealgebra import Algebra, Verbatim

head_mth_map = {
    EQ: Algebra.__eq__,
    NE: Algebra.__ne__,
    LT: Algebra.__lt__,
    LE: Algebra.__le__,
    GT: Algebra.__gt__,
    GE: Algebra.__ge__,
    }

class Logic(Algebra):
    """ Represents n-ary predicate expressions.

    An expression ``predicate(*args)`` is hold in a pair::

      (<predicate constant or function>, args)

    The following constants are defined to represent predicate
    functions:

      EQ - equality predicate
      LT - less-than predicate


    ``Logic.__nonzero__`` returns lexicographic value of relational
    predicates, otherwise ``True``.

    """

    def __nonzero__(self, head_mth_get=head_mth_map.get):
        head, (lhs, rhs) = self.pair
        mth = head_mth_get(head)
        if mth is None:
            return True
        return mth(lhs, rhs)
        
    def as_verbatim(self):
        return Verbatim(self.head, self.data)

classes.Logic = Logic