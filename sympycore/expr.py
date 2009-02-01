# -*- coding: latin-1 -*-
"""
  This module implements extension type Expr that holds two Python
  objects, head and data, in a pair attribute.

  When adding new features to Expr class, make sure that these are
  added also to extension type Expr in src/expr_ext.c.

C Expr:

>>> from sympycore.expr_ext import *
>>> %timeit Expr(1,2)
10000000 loops, best of 3: 179 ns per loop
>>> e=Expr(1,2)
>>> %timeit h = e.head
10000000 loops, best of 3: 113 ns per loop
>>> %timeit h,d = e.pair
10000000 loops, best of 3: 141 ns per loop

Python Expr:

>>> from sympycore.expr import *
>>> %timeit Expr(1,2)
1000000 loops, best of 3: 988 ns per loop
>>> e=Expr(1,2)
>>> %timeit h = e.head
10000000 loops, best of 3: 119 ns per loop
>>> %timeit h,d = e.pair
10000000 loops, best of 3: 139 ns per loop
"""
# Author: Pearu Peterson
# Created: March 2008

__all__ = ['Expr', 'Pair']

def init_module(m):
    from .core import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class Expr(object):
    """Represents an symbolic expression in a pair form: (head, data)	
                									
The pair (head, data) is saved in an attribute ``pair``. The parts of
a pair, head and data, can be also accessed via ``head`` and ``data``
attributes, respectively. All three attributes are read-only.
  									
The head part is assumed to be an immutable object.  The data part can
be either an immutable object or Python dictionary.  In the former
case, the hash value of Expr instance is defined as::
  									
    hash((<Expr>.head, <Expr>.

Otherwise, if ``data`` contains a Python dictionary, then the hash
value is defined as::
  									
    hash((<Expr>.head, frozenset(<Expr>.data.items())

If ``data`` is a Python list, then the hash value is::

  hash((<Expr>.head, tuple(<Expr>.data)))

WARNING: the hash value of an Expr instance is computed (and cached)
when it is used as a key to Python dictionary. This means that the
instance content MUST NOT be changed after the hash is computed.  To
check if it is safe to change the ``data`` dictionary, use
``is_writable`` attribute that returns True when the hash value has
not been computed::
  									
    <Expr>.is_writable -> True or False				
  									
There are two ways to access the parts of a Expr instance from	
Python::								
  									
    a = Expr(<head>, <data>)					
    head, data = a.head, a.data     - for backward compatibility	
    head, data = a.pair             - fastest way			

When Expr constructor is called with one argument, say ``x``, then
``<Expr subclass>.convert(x)`` will be returned.

This is Python version of Expr type.
"""

    __slots__ = ['head', 'data', 'pair', '_hash']

    def __init__(self, *args):
        if len(args)==1:
            obj = self.convert(args[0])
            self.pair = obj.pair
            self._hash = obj._hash
        elif len(args)==2:
            self.pair = args
            self._hash = None
        else:
            raise TypeError("%s requires 1 or 2 arguments but got %r" % (type(self), len(args)))

    def __repr__(self):
        return '%s%r' % (type(self).__name__, self.pair)

    def __hash__(self):
        """ Compute hash value.
        
        Different from expr_ext.Expr, an exception is raised when data
        dictionary values contain dictionaries.
        """
        h = self._hash
        if h is None:
            pair = self.pair
            obj = self.as_lowlevel()
            if obj is not pair:
                h = hash(obj)
            else:
                head, data = pair
                tdata = type(data)
                if tdata is dict:
                    h = hash((head, frozenset(data.iteritems())))
                elif tdata is list:
                    h = hash((head, tuple(data)))
                else:
                    h = hash(pair)
            self._hash = h
        return h

    @property
    def is_writable(self, _writable_types = (list, dict)):
        if self._hash is None:
            data = self.pair[1]
            tdata = type(data)
            if tdata in _writable_types:
                return True
            if tdata is Pair:
                return data.is_writable
        return False

    @property
    def head(self):
        return self.pair[0]

    @property
    def data(self):
        return self.pair[1]

    # Pickle support:
    def _sethash(self, hashvalue):
        """ Set hash value for the object.

        If hashvalue==-1, then the hash value will be reset.

        Used by pickle support in sympycore.core._reconstruct. DO NOT
        use this method directly.
        """
        if hashvalue==-1:
            self._hash = None
        else:
            self._hash = hashvalue

    def __reduce__(self):
        # see also _reconstruct function in sympycore/core.py
        version = 3
        from sympycore.core import _reconstruct
        if version==1:
            hashvalue = self._hash
            if hashvalue is None:
                hashvalue = -1
            state = (type(self), self.pair, hashvalue)
        elif version==2 or version==3:
            hashvalue = self._hash
            if hashvalue is None:
                hashvalue = -1
            cls = type(self)
            typ = type(cls)
            try:
                args = typ.__getinitargs__(cls)
            except AttributeError:
                args = None
            if args is None:
                # either metaclass does not define __getinitargs__ method
                # or cls has no metaclass
                state = (cls, self.pair, hashvalue)
            else:
                state = ((typ, args), self.pair, hashvalue)
        else:
            raise NotImplementedError('pickle state version %s' % (version))
        return  _reconstruct, (version, state)

    def __nonzero__(self):
        # Note that `not cls(MUL, [])` would return True while `cls(MUL, [])==1`.
        # So, must use as_lowlevel:
        obj = self.as_lowlevel()
        if obj is not self.pair:
            return not not obj
        return not not self.data

    def as_lowlevel(self):
        """ Return self as low-level object instance that will be used
        in comparison and in hash computation.

        By default, as_lowlevel uses heads to_lowlevel(cls, data, pair)
        method but since as_lowlevel is a most frequently called
        method then for some heads the corresponding code is copied
        here. The default return value is a pair tuple for composite
        objects and data part for atomic objects. The as_lowlevel
        method may also return an Expr instance but not self
        (otherwise infinite recurrsion will occur).

        See __hash__, __nonzero__ method for more details how the
        results of as_lowlevel method are interpreted.
        """
        head, data = pair = self.pair
        if head is NUMBER or head is SYMBOL or head is SPECIAL:
            return data
        elif head is MUL or head is DIV:
            n = len(data)
            if n==0:
                return 1
            if n==1:
                return data[0]
        elif head is ADD or head is SUB:
            n = len(data)
            if n==0:
                return 0
            if n==1:
                return data[0]
        elif head is POW:
            base, exp = data
            if exp==0 or base==1:
                return 1
            if exp==1:
                return base
        elif head is TERM_COEFF:
            term, coeff = data
            if coeff==0:
                return 0
            if coeff==1:
                return term
            if term==1:
                return coeff
        elif head is TERM_COEFF_DICT:
            n = len(data)
            if n==0:
                return 0
            if n==1:
                return type(self)(TERM_COEFF, dict_get_item(data))
        elif head is BASE_EXP_DICT:
            n = len(data)
            if n==0:
                return 1
            if n==1:
                return type(self)(POW, dict_get_item(data))
        else:
            return head.to_lowlevel(type(self), data, pair)
        return pair

    for _item in dict(__eq__ = '==', __ne__ = '!=',
                      __lt__ = '<', __le__ = '<=',
                      __gt__ = '>', __ge__ = '>=',
                      ).items():
        exec '''
def %s(self, other):
    if type(self) is type(other):
        other = other.as_lowlevel()
    return self.as_lowlevel() %s other
''' % _item

    def _add_item(self, key, value):
        # value must be non-zero
        head, data = self.pair
        assert type(data) is dict and value
        c = data.get(key)
        if c is None:
            data[key] = value
        else:
            c = c + value
            if c:
                data[key] = c
            else:
                del data[key]

    def _sub_item(self, key, value):
        # value must be non-zero
        head, data = self.pair
        assert type(data) is dict and value
        c = data.get(key)
        if c is None:
            data[key] = -value
        else:
            c = c - value
            if c:
                data[key] = c
            else:
                del data[key]

    def _add_dict(self, d):
        head, data = self.pair
        assert type(data) is dict
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value
            else:
                c = c + value
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _sub_dict(self, d):
        head, data = self.pair
        assert type(data) is dict
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = -value
            else:
                c = c - value
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _add_dict2(self, d, coeff):
        head, data = self.pair
        assert type(data) is dict,`type(data)`
        assert type(d) is dict,`type(d)`
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value * coeff
            else:
                c = c + value * coeff
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _add_dict3(self, d):
        head, data = self.pair
        assert type(data) is dict
        assert type(d) is dict
        cls = type(self)
        result = None
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value
            else:
                c = c + value
                if type(c) is cls and c.head is NUMBER:
                    c = c.data
                if c:
                    if key.head is NUMBER:
                        result = self.handle_numeric_item(result, key, c)
                    else:
                        data[key] = c
                else:
                    del data[key]
        return result

    def handle_numeric_item(self, result, key, value):
        """ Internal method.

        The method is called from the <Expr instance>._add_dict3(d) method
        when::
        
          <Expr instance>.data[key] = value

        needs to be executed but is left to the call::

          <Expr instance>.handle_numeric_method(result, key, value)

        to handle when key.head is NUMBER and value is non-zero
        low-level number. Note that handle_numeric_method is responsible
        for calling::
        
          del <Expr instance>.data[key]

        if it does not reset ``<Expr instance>.data[key]``.

        The handle_numeric_item() method may change the value of ``result``
        (that is returned by the _add_dict3() method) by returning new
        value. Initially ``result`` is ``None``.
        """
        self.data[key] = value
        return result

    def canonize_FACTORS(self):
        data = self.data
        l = len(data)
        if l==0:
            return self.one
        if l==1:
            t, c = data.items()[0]
            if c==1:
                return t
            if t==self.one:
                return t
        return self

    def canonize_TERMS(self):
        data = self.data
        l = len(data)
        if l==0:
            return self.zero
        if l==1:
            t, c = data.items()[0]
            if c==1:
                return t
            if t==self.one:
                return type(self)(NUMBER, c)
        return self

class Pair(Expr):

    def __eq__(self, other):
        return self.pair == other

    def __len__(self):
        return 2
    def __getitem__(self, index):
        return self.pair[index]

def dict_add_item(d, key, value):
    c = d.get(key)
    if c is None:
        d[key] = value
    else:
        c = c + value
        if c:
            d[key] = c
        else:
            del d[key]

def dict_get_item(d):
    return d.items()[0]

def dict_add_dict(dict1, dict2):
    for key, value in dict2.iteritems():
        c = dict1.get(key)
        if c is None:
            dict1[key] = value
        else:
            c = c + value
            if c:
                dict1[key] = c
            else:
                del dict1[key]

def dict_sub_dict(dict1, dict2):
    for key, value in dict2.iteritems():
        c = dict1.get(key)
        if c is None:
            dict1[key] = -value
        else:
            c = c - value
            if c:
                dict1[key] = c
            else:
                del dict1[key]

def dict_mul_dict(d, dict1, dict2):
    for t1,c1 in dict1.iteritems():
        for t2,c2 in dict2.iteritems():
            t = t1 * t2
            c12 = c1 * c2
            c = d.get(t)
            if c is None:
                d[t] = c12
            else:
                c = c + c12
                if c:
                    d[t] = c
                else:
                    del d[t]
    
def dict_mul_value(d, value):
    for t, c in d.items():
        d[t] = c*value
