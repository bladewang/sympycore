"""This file is generated by the sympycore/basealgebra/mk_pairs.py script.
Do not change this file directly!!!
"""

from ..utils import NUMBER, SYMBOL, TERMS, FACTORS, RedirectOperation



def add_method(self, other, active=True, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if type(other) is not cls:
        if isinstance(other, cls.coefftypes):
            if lhead is NUMBER:
                #ADD_VALUE_NUMBER(VALUE=other, RHS=self)
                obj = new(cls)
                obj.head = NUMBER
                obj.data = other + self.data
                return obj
            elif lhead is TERMS:
                #ADD_VALUE_TERMS(VALUE=other, RHS=self)
                try:
                    if not other:
                        return self
                except RedirectOperation:
                    if active:
                        return self._add_active(other)
                pairs = dict(self.data)
                one = cls.one
                b = pairs.get(one)
                if b is None:
                    pairs[one] = other
                else:
                    c = b + other
                    try:
                        if c:
                            pairs[one] = c
                        else:
                            del pairs[one]
                            if not pairs:
                                return cls.zero
                    except RedirectOperation:
                        pairs[one] = c
                obj = new(cls)
                obj.head = TERMS
                obj.data = pairs
                return obj
            else:
                #ADD_VALUE_SYMBOL(VALUE=other, RHS=self)
                try:
                    if not other:
                        return self
                except RedirectOperation:
                    if active:
                        return self._add_active(other)
                obj = new(cls)
                obj.head = TERMS
                obj.data = {cls.one: other, self: 1}
                return obj
        other = cls.convert(other, False)
        if other is NotImplemented:
            return other
    rhead = other.head
    if lhead is NUMBER:
        if rhead is NUMBER:
            #ADD_NUMBER_NUMBER(LHS=self, RHS=other)
            #ADD_VALUE_NUMBER(VALUE=self.data, RHS=other)
            obj = new(cls)
            obj.head = NUMBER
            obj.data = self.data + other.data
            return obj
        elif rhead is TERMS:
            #ADD_NUMBER_TERMS(LHS=self, RHS=other)
            #ADD_VALUE_TERMS(VALUE=self.data, RHS=other)
            try:
                if not self.data:
                    return other
            except RedirectOperation:
                if active:
                    return other._add_active(self.data)
            pairs = dict(other.data)
            one = cls.one
            b = pairs.get(one)
            if b is None:
                pairs[one] = self.data
            else:
                c = b + self.data
                try:
                    if c:
                        pairs[one] = c
                    else:
                        del pairs[one]
                        if not pairs:
                            return cls.zero
                except RedirectOperation:
                    pairs[one] = c
            obj = new(cls)
            obj.head = TERMS
            obj.data = pairs
            return obj
        else:
            #ADD_NUMBER_SYMBOL(LHS=self, RHS=other)
            #ADD_VALUE_SYMBOL(VALUE=self.data, RHS=other)
            try:
                if not self.data:
                    return other
            except RedirectOperation:
                if active:
                    return other._add_active(self.data)
            obj = new(cls)
            obj.head = TERMS
            obj.data = {cls.one: self.data, other: 1}
            return obj
    elif lhead is TERMS:
        if rhead is NUMBER:
            #ADD_NUMBER_TERMS(LHS=other, RHS=self)
            #ADD_VALUE_TERMS(VALUE=other.data, RHS=self)
            try:
                if not other.data:
                    return self
            except RedirectOperation:
                if active:
                    return self._add_active(other.data)
            pairs = dict(self.data)
            one = cls.one
            b = pairs.get(one)
            if b is None:
                pairs[one] = other.data
            else:
                c = b + other.data
                try:
                    if c:
                        pairs[one] = c
                    else:
                        del pairs[one]
                        if not pairs:
                            return cls.zero
                except RedirectOperation:
                    pairs[one] = c
            obj = new(cls)
            obj.head = TERMS
            obj.data = pairs
            return obj
        elif rhead is TERMS:
            #ADD_TERMS_TERMS(LHS=self, RHS=other)
            pairs = dict(self.data)
            get = pairs.get
            for t,c in other.data.iteritems():
                b = get(t)
                if b is None:
                    pairs[t] = c
                else:
                    c = b + c
                    try:
                        if c:
                            pairs[t] = c
                        else:
                            del pairs[t]
                    except RedirectOperation:
                        pairs[t] = c
            if not pairs:
                return cls.zero
            elif len(pairs)==1:
                t, c = pairs.items()[0]
                if c==1:
                    return t
                if t==cls.one:
                    return cls.convert(c)
            obj = new(cls)
            obj.head = TERMS
            obj.data = pairs
            return obj
        else:
            #ADD_TERMS_SYMBOL(LHS=self, RHS=other)
            pairs = dict(self.data)
            b = pairs.get(other)
            if b is None:
                pairs[other] = 1
            else:
                c = b + 1
                try:
                    if c:
                        if len(pairs)==1:
                            if c==1:
                                return other
                        pairs[other] = c
                    else:
                        del pairs[other]
                        if not pairs:
                            return cls.zero
                        if len(pairs)==1:
                            t, c = pairs.items()[0]
                            if c==1:
                                return t
                            if t==cls.one:
                                return cls.convert(c)
                except RedirectOperation:
                    pairs[other] = c
            obj = new(cls)
            obj.head = TERMS
            obj.data = pairs
            return obj
    else:
        if rhead is NUMBER:
            #ADD_NUMBER_SYMBOL(LHS=other, RHS=self)
            #ADD_VALUE_SYMBOL(VALUE=other.data, RHS=self)
            try:
                if not other.data:
                    return self
            except RedirectOperation:
                if active:
                    return self._add_active(other.data)
            obj = new(cls)
            obj.head = TERMS
            obj.data = {cls.one: other.data, self: 1}
            return obj
        elif rhead is TERMS:
            #ADD_TERMS_SYMBOL(LHS=other, RHS=self)
            pairs = dict(other.data)
            b = pairs.get(self)
            if b is None:
                pairs[self] = 1
            else:
                c = b + 1
                try:
                    if c:
                        if len(pairs)==1:
                            if c==1:
                                return self
                        pairs[self] = c
                    else:
                        del pairs[self]
                        if not pairs:
                            return cls.zero
                        if len(pairs)==1:
                            t, c = pairs.items()[0]
                            if c==1:
                                return t
                            if t==cls.one:
                                return cls.convert(c)
                except RedirectOperation:
                    pairs[self] = c
            obj = new(cls)
            obj.head = TERMS
            obj.data = pairs
            return obj
        else:
            #ADD_SYMBOL_SYMBOL(LHS=self, RHS=other)
            obj = new(cls)
            obj.head = TERMS
            if self == other:
                obj.data = {self: 2}
            else:
                obj.data = {self: 1, other: 1}
            return obj
    
