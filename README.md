simbool
=======

A sound, fast and incomplete boolean expression simplifier.
	
	>> from simbool.proposition import Prop
	>> from simbool.simplify import simplify
	
	# Creating 3 atomic propositions
	>> A, B, C = [Prop(x) for x in "ABC"]
	
	# Simplify some expression
	>> simplify(~A | (C & (~(B & ~C) | A)))
	~A | C
	
	# Proving a simple theorem ( > is the logical implication)
	>> P = (A > B) | (B > A)
	>> simplify(P)
	True	

	# Proving transitivity of implication
	>> P = ((A > B) & (B > C)) > (A > C)
	>> simplify(P)
	True
	
	# Proving another more complex theorem
	>> P = ((A > B) & (B > A)) > ((A & B) | ~(A | B))
	>> simplify(P)
	True

This is *not* based on the Quine-McCluskey algorithm.
Instead, it applies various formal simplification steps 
until reaching a fixed point. The output is guaranted to be
at most as complex as the input.

Where it currently fails
------------------------
	>> P = (A & ~B) | ((A | C) & B)
	# Should simplify into:
	A | (C & B)
		
	>> P = (C & A) | (C & B) | (A & ~B)
	# Should simplify into one of the following:
	(C & B) | (A & ~B)
	(A | B) & (~B | C)
