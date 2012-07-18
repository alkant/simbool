from proposition import Prop

__falseProp = Prop(False)
__trueProp = Prop(True)

def simplify_term(P):
    """negation-atom: ~True -> False; ~False -> True
    negation-elimination: ~~Prop -> Prop
    Unary op-elimination: (|Prop) -> Prop; (&Prop) -> Prop
    false-disjunction: False | Prop -> Prop
    true-disjunction: True | Prop -> True
    false-conjunction: False & Prop -> False
    true-conjunction: True & Prop -> Prop
    opposite-elimination-conjunction: ~Prop1 | Prop2 -> True if Prop1 == Prop2
    opposite-elmination-disjunction: ~Prop1 & Prop2 -> False if Prop1 == Prop2"""
    if P.atomic:
        return P
    
    if P.get_op() == '~': 
        sub = P.get_terms()[0]
        if sub.atomic:
            if sub.name == True:
                return __falseProp
            if sub.name == False:
                return __trueProp
        if sub.get_op() == '~':
            return sub.get_terms()[0]
        return P
    
    if len(P.get_terms()) == 1:
        return P.get_terms()[0]

    def breakdown(P):
        positive = set()
        negative = set()
        negative_with_negation = set()
        for e in P.get_terms():
            if e.is_positive():
                positive.add(e)
            else:
                assert(e.get_op() == '~')
                negative.add(e.get_terms()[0])
                negative_with_negation.add(e)
        return positive, negative, negative_with_negation
    
    if P.get_op() == '&':
        pos, neg, negn = breakdown(P)

        if __falseProp in pos:
            return __falseProp

        if len(pos & neg) > 0:
            return __falseProp
        
        if __trueProp in pos:
            if len(pos) > 1 or len(neg) > 0:
                pos.remove(__trueProp)
            else:
                return __trueProp
        terms = list(pos)+list(negn)
        if len(terms) == 1:
            return terms[0]
        return Prop('&', *terms)

    if P.get_op() == '|':
        pos, neg, negn = breakdown(P)

        if __trueProp in pos:
            return __trueProp

        if len(pos & neg) > 0:
            return __trueProp
        
        if __falseProp in pos:
            if len(pos) > 1 or len(neg) > 0:
                pos.remove(__falseProp)
            else:
                return __falseProp
        
        terms = list(pos)+list(negn)
        if len(terms) == 1:
            return terms[0]
        
        return Prop('|', *terms)
    
    assert(False)

def associative_collect(P):
    return __associative_collect(P)[0]

def __associative_collect(P, sym = None):
    if P.is_literal():
        return [P]

    if P.get_op() == '~':
        return [Prop('~', *__associative_collect(P.get_terms()[0]))]

    if sym != P.get_op():
        col = []
        for e in P.get_terms():
            col += __associative_collect(e, P.get_op())
        return [Prop(P.get_op(), *col)]
    else:
        col = []
        for e in P.get_terms():
            r = __associative_collect(e, sym)
            col += r
        return col
    
    assert(False)

def simplify_everywhere(P):
    res = __simplify_everywhere(P)
    res_old = res
    while True:
        res = __simplify_everywhere(res)
        if res_old == res:
            break
        res_old = res
    return res

def __simplify_everywhere(P):
    if P.atomic:
        return P
    
    simplified = simplify_term(P)

    if simplified.atomic:
        return simplified
    
    return Prop(simplified.get_op(), *[__simplify_everywhere(sub) for sub in simplified.get_terms()])

def push_neg(P):
    if P.is_literal():
        return P

    if P.get_op() in ['&', '|']:
        return Prop(P.get_op(), *[push_neg(sub) for sub in P.get_terms()])
    
    if P.get_op() == '~':
        term = P.get_terms()[0]
        if term.is_atomic():
            return S

        if term.get_op() == '&':
            return Prop('|', *[push_neg(~sub) for sub in term.get_terms()])
        if term.get_op() == '|':
            return Prop('&', *[push_neg(~sub) for sub in term.get_terms()])
        if term.get_op() == '~':
            return push_neg(term.get_terms()[0])
    
    assert(False)

def propagate_literals(P, domain=set()): #TODO
    positive = set()
    negative = set()
    for e in domain:
        if e is __falseProp:
            return __falseProp
        if e.is_atomic():
            positive.add(e)
        else:
            negative.add(~e)
    if len(positive & negative) > 0:
        return __falseProp
    
    if P.is_literal():
        if simplify_term(~P) in domain:
            return __falseProp
        if P in domain:
            return __trueProp
        return P

    if P.get_op() in ['~']:
        print("Try running push_neg() first.")
        return Prop('~', propagate_literals(P.get_terms()[0]))

    if P.get_op() in ['&', '|']:
        new_literals = []
        other_terms = []
        new_domain = set()
        for e in P.get_terms():
            if e.is_literal():
                if simplify_term(~e) in domain:
                    new_literals.append(__falseProp)
                else:
                    if e in domain:
                        new_literals.append(__trueProp)
                    else:
                        new_literals.append(e)
                if P.get_op() == '&':
                    new_domain.add(e)
                else:
                    new_domain.add(simplify_term(~e))
            else:
                other_terms.append(e)

        for e in domain:
            new_domain.add(e)
        
        return Prop(P.get_op(), *(new_literals + [propagate_literals(sub, new_domain) for sub in other_terms]))

    assert(False)

def simplify_basic(P):
    res = associative_collect(P)
    res = simplify_everywhere(res)
    res = push_neg(res)
    res = associative_collect(res)
    return simplify_everywhere(res)

def simplify(P):
    """Apply various strategies until reaching fixed point."""
    res = simplify_basic(P)
    
    old = res
    res = propagate_literals(res)
    while True:
        res = associative_collect(res)
        res = simplify_everywhere(res)
        if old == res:
            break
        old = res
        res = propagate_literals(res)

    return res
