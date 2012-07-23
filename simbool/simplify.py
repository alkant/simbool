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

def propagate_hypothesis(P, domain=set()):
    positive = set()
    negative = set()
    for e in domain:
        if e == __falseProp:
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
        return Prop('~', propagate_hypothesis(P.get_terms()[0], domain))

    if P.get_op() in ['&', '|']:
        new_terms = []
        old_terms = []
        new_domain = set()
        for e in P.get_terms():
            if simplify_term(~e) in domain:
                new_terms.append(__falseProp)
            else:
                if e in domain:
                    new_terms.append(__trueProp)
                else:
                    if e.is_literal():
                        new_terms.append(e)
                    else:
                        old_terms.append(e)

            if e.is_literal():
                if P.get_op() == '&':
                    new_domain.add(e)
                else:
                    new_domain.add(simplify_term(~e))

        for e in domain:
            new_domain.add(e)
        
        return Prop(P.get_op(), *(new_terms + [propagate_hypothesis(sub, new_domain) for sub in old_terms]))

    assert(False)

def factor_local(P):
    if P.is_literal():
        return P

    subterms = []
    for term in P.get_terms():
        if term.is_literal():
            if term.is_atomic():
                subterms.append([{term}, {term}, term])
            else:
                subterms.append([{simplify_term(~term)}, {term}, term])
        else:
            sub_p = set()
            sub_p_raw = set()
            for sub in term.get_terms():
                if sub.is_positive():
                    sub_p.add(sub)
                    sub_p_raw.add(sub)
                else:
                    sub_p.add(simplify_term(~sub))
                    sub_p_raw.add(sub)
            subterms.append([sub_p, sub_p_raw, term])
    
    counts = {}
    counts_raw = {}
    for s, r, _ in subterms:
        for ss in s:
            if ss not in counts:
                counts[ss] = 0
            counts[ss] += 1
        for sr in r:
            if sr not in counts_raw:
                counts_raw[sr] = 0
            counts_raw[sr] += 1
    
    sp = counts.keys()
    sp.sort(key = lambda x: counts[x], reverse=True)
    if counts[sp[0]] <= 2:
        sp = counts_raw.keys()
        sp.sort(key = lambda x: counts_raw[x], reverse=True)
        if counts_raw[sp[0]] < 2:
            return P
        else:
            to_keep = [x[2] for x in subterms if sp[0] not in x[1]]
            to_factor = Prop(P.get_op(), *[x[2] for x in subterms if sp[0] in x[1]])
            return Prop(P.get_op(), (sp[0] & propagate_hypothesis(to_factor, {sp[0]})) | \
                                     (~sp[0] & propagate_hypothesis(to_factor, {simplify_term(~sp[0])})), *to_keep)
    
    to_keep = [x[2] for x in subterms if sp[0] not in x[0]]
    to_factor = Prop(P.get_op(), *[x[2] for x in subterms if sp[0] in x[0]])
    return Prop(P.get_op(), (sp[0] & propagate_hypothesis(to_factor, {sp[0]})) | \
                            (~sp[0] & propagate_hypothesis(to_factor, {simplify_term(~sp[0])})), *to_keep)

def factor_at_top(P):
    if P.is_literal():
        return P
    
    factored = factor_local(P)

    if factored is not P:
        return factored
    
    return Prop(P.get_op(), *[factor_at_top(sub) for sub in P.get_terms()])

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
    res = propagate_hypothesis(res)
    while True:
        res = associative_collect(res)
        res = simplify_everywhere(res)
        if old == res:
            res = factor_at_top(res)
            if res == old:
                break
            res = simplify_everywhere(res)
            res = associative_collect(res)
        old = res
        res = propagate_hypothesis(res)

    return res
    
def stats(P, counts=None):
    if counts is None:
        counts = dict()

    if P.is_literal():
        if P.is_positive():
            if P not in counts:
                counts[P] = [0, 0]
            counts[P][0] += 1
        else:
            pos = P.get_terms()[0]
            if pos not in counts:
                counts[pos] = [0, 0]
            counts[pos][1] += 1
        return counts

    if P.oper in ['&', '|']:
        for sub in P.terms:
            stats(sub, counts)
        return counts

    if P.oper == '~':
        for sub in P.terms:
            nc = stats(sub)
            for e in nc:
                if e not in counts:
                    counts[e] = [0, 0]
                counts[e][0] += nc[e][1]
                counts[e][1] += nc[e][0]
        return counts

    raise NameError("ERROR")
