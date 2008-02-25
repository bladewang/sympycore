#!/usr/bin/env python
#
# Created by Pearu Peterson in Febuary 2008
#

import os

def preprocess(source, tmp_cache=[1]):
    result = []
    for line in source.splitlines():
        if line.lstrip().startswith('@'):
            prefix, rest = line.split('@',1)
            i = rest.index('(')
            name = rest[:i]
            tmp_cache[0] += 1
            d = {'TMP':'_tmp%s' % (tmp_cache[0])}
            try:
                for arg in rest.strip()[i+1:-1].split(';'):
                    key, value = arg.split('=',1)
                    d[key.strip()] = value.strip()
            except Exception, msg:
                #print `rest`
                print '%s (while processing %r)' % (msg, line.lstrip())
                continue
            try:
                templ = eval(name, globals(), {})
            except NameError, msg:
                templ = '@' + rest
                print 'NameError: %s (while processing %r)' % (msg, line.strip())
            else:
                if '@' in templ:
                    templ = preprocess(templ)
            result.append(prefix + '#' + rest)
            try:
                templ_d = templ % d
            except Exception, msg:
                print '%s (while processing %r)' % (msg, line.lstrip())
                #print d, `templ`
                continue
            for l in templ_d.splitlines():
                result.append(prefix + l)
        else:
            result.append(line)
    return '\n'.join(result)

cwd = os.path.abspath(os.path.dirname(__file__))
targetfile_py = os.path.join(cwd,'pairs_iops.py')

template = '''\
"""
This file is generated by the sympycore/basealgebra/mk_pairs_iops.py script.
DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..arithmetic.numbers import Complex, Float, FractionTuple, try_power
from ..utils import NUMBER, TERMS, FACTORS

'''

NEWINSTANCE = '''\
%(OBJ)s = new(cls)
%(OBJ)s.head = %(HEAD)s
%(OBJ)s.data = %(DATA)s
'''
RETURN_NEW = '''\
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=%(HEAD)s; DATA=%(DATA)s)
return %(TMP)s
'''

IF_CHECK_INT = 'if %(T)s is int or %(T)s is long:'
ELIF_CHECK_INT = 'elif %(T)s is int or %(T)s is long:'
IF_CHECK_REAL = 'if %(T)s is int or %(T)s is long or %(T)s is FractionTuple or %(T)s is float or %(T)s is Float:'
IF_CHECK_COMPLEX = 'if %(T)s is cls or %(T)s is complex:'

ELIF_CHECK_NUMBER = 'elif %(T)s is int or %(T)s is long or %(T)s is FractionTuple or %(T)s is float or %(T)s is Float or %(T)s is Complex or %(T)s is complex:'

ADD_TERM_VALUE_DICT='''\
%(TMP)s = %(DICT_GET)s(%(TERM)s)
if %(TMP)s is None:
    %(DICT)s[%(TERM)s] = %(SIGN)s %(VALUE)s
else:
    %(TMP)s = %(TMP)s %(SIGN)s %(VALUE)s
    if %(TMP)s:
        %(DICT)s[%(TERM)s] = %(TMP)s
    else:
        del %(DICT)s[%(TERM)s]
'''

MUL_FACTOR_VALUE_DICT='''\
%(TMP)s = %(DICT_GET)s(%(FACTOR)s)
if %(TMP)s is None:
    %(DICT)s[%(FACTOR)s] = %(SIGN)s %(VALUE)s
else:
    %(TMP)s = %(TMP)s %(SIGN)s %(VALUE)s
    if type(%(TMP)s) is cls and %(TMP)s.head is NUMBER:
        %(TMP)s = %(TMP)s.data
    if %(TMP)s:
        if %(FACTOR)s.head is NUMBER:
            del %(DICT)s[%(FACTOR)s]
            z, sym = try_power(%(FACTOR)s.data, %(TMP)s)
            if sym:
                for t1, c1 in sym:
                    @NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                    @ADD_TERM_VALUE_DICT(DICT=%(DICT)s; DICT_GET=%(DICT_GET)s; TERM=tt; VALUE=c1; SIGN=+)
            %(NUMBER)s = %(NUMBER)s * z
            
        else:
            %(DICT)s[%(FACTOR)s] = %(TMP)s
    else:
        del %(DICT)s[%(FACTOR)s]
'''

def main():
    f = open(targetfile_py, 'w')
    print >> f, template
    print >> f, preprocess('''

def return_terms(cls, pairs, new=object.__new__):
    if not pairs:
        return cls.zero
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return cls.convert(c)
    @RETURN_NEW(HEAD=TERMS; DATA=pairs)

def return_factors(cls, pairs, new=object.__new__):
    if not pairs:
        return cls.one
    elif len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return t
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)

def inplace_add(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = obj.data
            if value:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+)
        elif head is TERMS:
            for t,c in obj.data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=+)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=+)
    @ELIF_CHECK_NUMBER(T=tobj)
        if obj:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=+)
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_add2(cls, obj, coeff, pairs, pairs_get, one):
    if not coeff:
        return
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = coeff * obj.data
            if value:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+)
        elif head is TERMS:
            for t,c in obj.data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=coeff*c; SIGN=+)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=coeff; SIGN=+)
    @ELIF_CHECK_NUMBER(T=tobj)
        value = coeff * obj
        if value:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+)
    else:
        inplace_add2(cls, cls.convert(obj), coeff, pairs, pairs_get, one)

def inplace_sub(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = obj.data
            if value:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=-)
        elif HEAD is TERMS:
            for t,c in obj.data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=-)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=-)
    @ELIF_CHECK_NUMBER(T=tobj)
        if obj:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=-)
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_mul(cls, obj, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            return obj.data
        elif head is TERMS:
            data = obj.data
            if len(data)==1:
                t, number = data.items()[0]
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=1; SIGN=+; NUMBER=number)
                return number
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; NUMBER=number)
            return number
        elif head is FACTORS:
            number = 1
            for t, c in obj.data.iteritems():
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c; SIGN=+; NUMBER=number)
            return number
        else:
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; NUMBER=number)
            return number
    @ELIF_CHECK_NUMBER(T=tobj)
        return obj
    else:
        return inplace_mul(cls, cls.convert(obj), pairs, pairs_get)

def inplace_mul2(cls, obj, exp, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    if not exp:
        return 1
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            return obj.data ** exp
        elif head is TERMS:
            data = obj.data
            if len(data)==1:
                t, number = data.items()[0]
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=exp; SIGN=+; NUMBER=number)
                return number
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; NUMBER=number)
            return number
        elif head is FACTORS:
            number = 1
            for t, c in obj.data.iteritems():
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c*exp; SIGN=+; NUMBER=number)
            return number
        else:
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; NUMBER=number)
            return number
    @ELIF_CHECK_NUMBER(T=tobj)
        return obj ** exp
    else:
        return inplace_mul2(cls, cls.convert(obj), exp, pairs, pairs_get)

    ''')

if __name__=='__main__':
    main()
