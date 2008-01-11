
import types

from ..core import classes
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, ADD, MUL, SYMBOL, NUMBER

iterator_types = (type(iter([])), type(iter(())), type(iter(frozenset())),
                  type(dict().iteritems()), types.GeneratorType)

class PairsCommutativeRing(BasicAlgebra):
    """ Contains generic methods to algebra classes that
    use Pairs.
    """
    def __new__(cls, obj, head=None):
        if head is None:
            return cls.convert(obj)
        return cls.element_classes[head](obj)

    @classmethod
    def Add(cls, seq):
        terms = cls.element_classes[ADD]({})
        one = cls.one
        zero_c = cls.zero_c
        one_c = cls.one_c
        a_cls = cls.convert
        for t in seq:
            t = a_cls(t)
            head = t.head
            if head is SYMBOL:
                terms._add_value(t, one_c, zero_c)
            elif head is NUMBER:
                terms._add_value(one, t.value, zero_c)
            elif head is ADD:
                terms._add_values(t, one_c, zero_c)
            elif head is MUL:
                terms._add_value(t, one_c, zero_c)
            else:
                raise TypeError(`t, head`)
        return terms.canonize_add()

    @classmethod
    def Mul(cls, seq):
        result = cls.element_classes[MUL]({})
        one = cls.one
        zero_e = cls.zero_e
        one_e = cls.one_e
        one_c = cls.one_c
        zero_c = cls.zero_c
        a_cls = cls.convert
        number = one_c
        for t in seq:
            t = a_cls(t)
            head = t.head
            if head is SYMBOL:
                result._add_value(t, one_e, zero_e)
            elif head is NUMBER:
                number = number * t.value
            elif head is ADD:
                result._add_value(t, one_e, zero_e)
            elif head is MUL:
                result._add_values(t, one_e, zero_e)
            else:
                raise TypeError(`t, head`)
        result = result.canonize_mul()
        if number==one_c:
            return result
        if result==one:
            return cls.element_classes[NUMBER](number)
        head = result.head
        if head is NUMBER:
            return cls.element_classes[NUMBER](result * number)
        if head is ADD:
            r = result.copy()
            r._multiply_values(number, one_c, zero_c)
            return r.canonize_add()
        return cls.element_classes[ADD]({result: number})

    def __radd__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            return other + self
        return NotImplemented

    def __rmul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            return other * self
        return NotImplemented

class Pairs(object):
    """ Base class for holding pairs (by default non-commutative).
    """
    def __new__(cls, pairs):
        if isinstance(pairs, cls):
            return pairs
        o = object.__new__(cls)
        o._pairs = pairs
        o._hash = None
        return o

    @property
    def pairs(self):
        """ Return pairs as a tuple.
        """
        pairs = self._pairs
        if not isinstance(pairs, tuple):
            self._pairs = pairs = tuple(pairs)
        return pairs

    def __iter__(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return len(pairs)
        return len(pairs)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.pairs == other.pairs
        return False

    #XXX: impl modification methods


class CommutativePairs(Pairs):
    """ Represents operands of an commutative operation.

      CommutativePairs(<pairs>)

    where <pairs> is a sequence or an iterator of pairs:

      (<expression>, <repetition>)

    Here <expression> must be hashable as internally the pairs are
    saved in Python dictionary for update efficiency.

    CommutativePairs instance is mutable until the moment its hash
    value is computed.

    The following methods are defined to modify the CommutativePairs
    instance:
      _add_value(rhs, one, zero)
        rhs must be usable as key

      _add_values(rhs, one, zero)
        rhs must be an iterable returning pairs

      _multiply_values(rhs, one, zero)
        rhs must be support multiplication with values

      _expand_multiply_values(rhs, one, zero)
        rhs must be an iterable returning pairs
        
      _add_keys(rhs, one, zero)
        rhs must support addition with keys
    """
    
    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def copy(self):
        return type(self)(self.pairs.copy())

    def __iter__(self):
        """ Return iterator of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        elif isinstance(pairs, Pairs):
            raise
            return pairs.pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        return len(pairs)

    def __hash__(self):
        h = self._hash
        if h is None:
            # Using frozenset hash algorithm to avoid creating
            # frozenset instance. It should be safe to have the
            # same hash value with the frozenset as dictionary
            # keys of self should never contain a frozenset.
            h = 1927868237
            h *= self.length()+1
            for t in self:
                h1 = hash(t)
                h ^= (h1 ^ (h1 << 16) ^ 89869747)  * 3644798167
            h = h * 69069 + 907133923
            self._hash = h
        return h

    def __str__(self):
        return '%s([%s])' % (self.__class__.__name__,
                             ', '.join(['(%s, %s)' % tc for tc in self.pairs.iteritems()]))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._pairs)

    def _add_value(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add value to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        b = pairs.get(rhs)
        if b is None:
            pairs[rhs] = one
        else:
            c = b + one
            if zero==c:
                del pairs[rhs]
            else:
                pairs[rhs] = c

    def _add_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if zero==c:
                    del pairs[t]
                else:
                    pairs[t] = c

    def _multiply_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t in pairs.keys():
            pairs[t] = pairs[t] * rhs

    def _expand_multiply_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot expand multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        self._pairs = d = {}
        if isinstance(rhs, iterator_types):
            seq1 = rhs
            seq2 = pairs.items()
        elif len(rhs) > len(pairs):
            seq1 = pairs.iteritems()
            seq2 = rhs
        else:
            seq1 = rhs
            seq2 = pairs.items()
        for t1, c1 in seq1:
            for t2, c2 in seq2:
                t = t1 * t2
                c = c1 * c2
                #XXX: make sure that t is not a number, it can be one though
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = b + c
                    if zero==c:
                        del d[t]
                    else:
                        d[t] = c

    def _add_keys(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add keys to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs        
        self._pairs = d = {}
        for t,c in pairs.items():
            d[t + rhs] = c
        self._pairs = d

    def canonize_add(self):
        pairs = self.pairs
        if not pairs:
            return self.zero
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if self.one_c==c:
                return t
            if self.one==t:
                return self.convert(c)
        return self

    def canonize_mul(self):
        pairs = self.pairs
        if not pairs:
            return self.one
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if self.one_e==c:
                return t
            if self.one==t:
                return t
        return self

    def as_primitive_add(self):
        l = []
        one_c = self.one_c
        one = self.one
        for t,c in self:
            if one_c==c:
                l.append(PrimitiveAlgebra(t))
            elif one==t:
                l.append(PrimitiveAlgebra(c))
            else:
                if c==-one_c:
                    l.append(-PrimitiveAlgebra(t))
                else:
                    l.append(PrimitiveAlgebra(c) * t)
        if len(l)==1:
            return l[0]
        r = PrimitiveAlgebra((ADD,tuple(l)))
        r.commutative_add = True
        return r

    def as_primitive_mul(self):
        l = []
        one_c = self.one_c
        for t,c in self:
            t = PrimitiveAlgebra(t)
            if one_c==c:
                l.append(t)
            else:
                l.append(t ** c)
        if len(l)==1:
            return l[0]
        r = PrimitiveAlgebra((MUL,tuple(l)))
        r.commutative_mul = True
        return r


            