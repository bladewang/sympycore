
from ...core import Basic, classes
from .function import Predicate

__all__ = ['And', 'Or', 'Xor', 'Implies', 'Equiv']

class And(Predicate):
    """ And(..) predicate.

    a & TRUE -> a
    a & FALSE -> FALSE
    a & (b & c) -> a & b & c
    a & a -> a
    a & ~a -> FALSE
    """
    # signature is initialized in __init__.py

    ordered_arguments = False

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, And):
                new_operants = new_operants.union(o.args)
                flag = True
            elif isinstance(o, bool):
                if not o:
                    return False
                flag = True
            else:
                n = len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in new_operants:
            if isinstance(o, classes.Not) and o.args[0] in new_operants:
                return False
        if not new_operants:
            return True
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        return        


class Or(Predicate):
    """
    a | TRUE -> TRUE
    a | FALSE -> a
    a | (b | c) -> a | b | c
    a | a -> a
    a | ~a -> TRUE
    """
    # signature is initialized in __init__.py

    ordered_arguments = False

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, Or):
                new_operants = new_operants.union(o.args)
                flag = True
            elif isinstance(o, bool):
                if o:
                    return True
                flag = True
            else:
                n=len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in new_operants:
            if isinstance(o, classes.Not) and o.args[0] in new_operants:
                return True
        if not new_operants:
            return False
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        return


class Xor(Predicate):
    """
    a ^ TRUE -> ~a
    a ^ FALSE -> a
    a ^ (b ^ c) -> a ^ b ^ c
    a ^ a -> FALSE
    a ^ ~a -> TRUE
    """
    # signature is initialized in __init__.py

    ordered_arguments = True

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return False
        if len(operants)==1:
            arg = operants[0]
            return arg
        if False in operants:
            return cls(*[o for o in operants if o is not False])
        new_operants = []        
        flag = False
        truth_index = 0
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if o: truth_index += 1
            elif isinstance(o, classes.Xor):
                flag = True
                new_operants.extend(o.args)
            else:
                new_operants.append(o)
        operants = new_operants
        new_operants = []
        for o in operants:
            if o not in new_operants:
                po = Not(o)
                if po in new_operants:
                    flag = True
                    truth_index += 1
                    new_operants.remove(po)
                else:
                    new_operants.append(o)
            else:
                new_operants.remove(o)
                flag = True
        if flag:
            if truth_index % 2:
                if new_operants:
                    new_operants[-1] = Not(new_operants[-1])
                else:
                    return True
            return cls(*new_operants)
        return
    

class Not(Predicate):
    # signature is initialized in __init__.py

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, bool):
            return not arg
        if isinstance(arg, classes.Not):
            return arg[0]


class Implies(Predicate):

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Not(lhs), rhs)


class Equiv(Predicate):

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Not(Xor(lhs, rhs))