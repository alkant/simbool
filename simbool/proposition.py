from __future__ import print_function

class Prop:
    def __init__(self, *args):
        """Proposition constructor.
        Prop(True), Prop(False) constructs the True and False atoms.
        Prop(name) constructs an atomic proposition.
        Prop('&', p1, p2, ...) constructs the conjunction of propositions p1, p2, ...
        Prop('|', p1, p2, ...) constructs the disjunction of propositions p1, p2, ...
        Prop('~', p) constructs the negation of proposition p.
        
        Built-in rewritings:
            redundance-elimination-union: Prop1 | Prop2 -> (|Prop1) if Prop1 == Prop2
            redundance-elimination-intersection: Prop1 & Prop2 -> (&Prop1) if Prop1 == Prop2"""
        if len(args) == 0:
            raise NameError("Malformed proposition.")
        
        if len(args) == 1:
            self.name = args[0]
            self.atomic = True

        if len(args) > 1:
            if args[0] not in ['&', '|', '~'] or \
                args[0] == '~' and len(args)>2:
                raise NameError("Malformed proposition: "+str(args)) 
            self.oper = args[0]
            self.terms = frozenset(args[1:])
            self.atomic = False

    def is_atomic(self):
        return self.atomic
    
    def is_positive(self):
        return self.atomic or (self.oper in ['&', '|'])

    def is_negative(self):
        return (not self.atomic) and (self.oper == '~')

    def is_literal(self):
        return self.atomic or \
                self.oper == '~' and [x.atomic for x in self.terms][0]
    
    def __eq__(self, other):
        """Syntactic equality testing. Fully commutative but not associative. 
        If True, then the two propositions are equal. If False, unsure."""
        if self.atomic:
            if other.atomic:
                return self.name == other.name
            return False
        if other.atomic:
            return False
        if self.oper == self.oper:
            return self.terms == other.terms
        return False
    
    def __ne__(self, other):
        return not (self == other)
    
    def __hash__(self):
        if '_hash' in self.__dict__:
            return self._hash
        if self.atomic:
            self._hash = hash(self.name)
            return self._hash
        self._hash = hash(hash(self.oper)^hash(self.terms))
        return self._hash
    
    def __str__(self):
        def no_parenthesing(s):
            return s.atomic or s.oper == '~'
        
        if self.atomic:
            return str(self.name)
        
        oper = self.oper
        if oper == '~':
            a = [x for x in self.terms][0]
            if no_parenthesing(a):
                return oper+str(a)
            return oper+'('+str(a)+')'
        
        if oper in ['&', '|']:
            subs = []
            for e in self.terms:
                if no_parenthesing(e):
                    subs.append(str(e))
                else:
                    subs.append('('+str(e)+')')
            assert(len(subs) > 0)
            if len(subs) == 1:
                return '('+oper+subs[0]+')'
            return (' '+oper+' ').join(subs)
        
        assert(False)

    def __and__(self, other):
        return Prop('&', self, other)

    def __rand__(self, other):
        return other.__and__(self)

    def __or__(self, other):
        return Prop('|', self, other)

    def __ror__(self, other):
        return other.__ror__(self)

    def __invert__(self):
        return Prop('~', self)

    def __gt__(self, other):
        """material implication."""
        return other | (~self)
    
    def __sub__(self, other):
        return self & ~other

    def __rsub__(self, other):
        return other.__sub__(self)

    def __repr__(self):
        return str(self)

    def get_op(self):
        return self.__dict__.get('oper', None)

    def get_terms(self):
        return [x for x in self.__dict__.get('terms', [None])]

    def size(self):
        if self.atomic:
            return 1
        return 1 + sum([x.size() for x in self.terms])
