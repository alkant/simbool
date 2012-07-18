import unittest
from proposition import *
from simplify import *

class TestSet(unittest.TestCase):
    def setUp(self):
        A = Prop('A')
        B = Prop('B')
        C = Prop('C')
        D = Prop('D')
        P = (C & ~D) | (D & ~C)
        T = Prop(True)
        F = Prop(False)

        self.cases = [T, F, A, ~T, ~F, ~A, 
                      A & F, F & A, A & T, T & A,
                      A & B, B & A, A | F, F | A,
                      T | A, A | T, A | B, B | A,
                      F | F, T | T, A | A,
                      F & F, T & T, A & A, 
                      P, ~~A, ~~P, ~~T, ~~F
                     ]

    def test_prop(self):
        A = Prop('A')
        B = Prop('B')
        C = Prop('C')
        D = Prop('D')
        P = (C & ~D) | (D & ~C)
        T = Prop(True)
        F = Prop(False)
        
        repr = ['True', 'False', 'A', '~True', '~False', '~A', 
                'A & False', 'False & A', 'A & True', 'A & True', 
                'A & B', 'A & B', 'A | False', 'False | A', 
                'A | True', 'A | True', 'A | B', 'A | B', 
                '(|False)', '(|True)', '(|A)',
                '(&False)', '(&True)', '(&A)',
                '(~C & D) | (C & ~D)', '~~A',
                '~~((~C & D) | (C & ~D))', '~~True', '~~False',
               ]
        
        new_commute = [T, F, A, ~T, ~F, ~A, 
                      F & A, A & F, T & A, A & T,
                      B & A, A & B, F | A, A | F,
                      A | T, T | A, B | A, A | B,
                      F | F, T | T, A | A,
                      F & F, T & T, A & A,
                      (~C & D) | (~D & C), ~~A,
                     ~~((~C & D) | (~D & C)), ~~T, ~~F,
                     ]
        
        atomic = [True, True, True, False, False, False,
                  False, False, False, False,
                  False, False, False, False,
                  False, False, False, False,
                  False, False, False,
                  False, False, False,
                  False, False, 
                  False, False, False,
                 ]

        i = 0
        for expr in self.cases:
            self.assertEqual(str(expr), repr[i])
            self.assertEqual(expr, new_commute[i])
            self.assertEqual(expr.is_atomic(), atomic[i])
            i += 1

    def test_simplify_term(self):
        A = Prop('A')
        B = Prop('B')
        C = Prop('C')
        D = Prop('D')
        P = (C & ~D) | (D & ~C)
        T = Prop(True)
        F = Prop(False)
        
        simp = ['True', 'False', 'A', 'False', 'True', '~A', 
                'False', 'False', 'A', 'A', 
                'A & B', 'A & B', 'A', 'A', 
                'True', 'True', 'A | B', 'A | B', 
                'False', 'True', 'A',
                'False', 'True', 'A',
                '(~C & D) | (C & ~D)', 'A',
                '(~C & D) | (C & ~D)', 'True', 'False',
               ]
        
        new_commute = [T, F, A, F, T, ~A, 
                      F, F, A, A,
                      B & A, A & B, A, A,
                      T, T, B | A, A | B,
                      F, T, A,
                      F, T, A,
                      (~C & D) | (~D & C), A,
                      (~C & D) | (~D & C), T, F,
                     ]
        
        atomic = [True, True, True, True, True, False,
                  True, True, True, True,
                  False, False, True, True,
                  True, True, False, False,
                  True, True, True,
                  True, True, True,
                  False, True,
                  False, True, True,
                 ]

        i = 0
        for expr in self.cases:
            expr = simplify_term(expr)
            self.assertEqual(str(expr), simp[i])
            self.assertEqual(expr, new_commute[i])
            self.assertEqual(expr.is_atomic(), atomic[i])
            i += 1

if __name__ == '__main__':
    unittest.main()
