simbool
=======

A sound, fast and incomplete boolean expression simplifier.
This is *not* based on the Quine-McCluskey algorithm.

	>> from simbool.proposition import Prop
	>> from simbool.simplify import simplify
	
	# Creating 3 atomic propositions
	>> A, B, C = [Prop(x) for x in "ABC"]
	
	# Proving a simple theorem
	>> P = (A > B) | (B > A)
	>> simplify(P)
	True	

	# Proving transitivity of implication
	>> P = ((A > B) & (B > C)) > (A > C)
	>> simplify(P)
	True
	
	# Simplify some expression
	>> simplify(~A | (C & (~(B & ~C) | A)))
	~A | C
