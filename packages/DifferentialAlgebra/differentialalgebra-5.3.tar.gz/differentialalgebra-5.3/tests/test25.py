# attributes

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_25(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [u,v])
        eq1 = Eq(Derivative(u(x,y),x), v(x,y))
        eq2 = Derivative(u(x,y),y) 
        eq3 = Derivative(v(x,y),y)
        C = RegularDifferentialChain ([eq1,eq2,eq3], R)
        Z = C.attributes ()
        self.assertEqual (Z, ['differential', 'prime', 'autoreduced', 'primitive', 'squarefree', 'coherent', 'normalized'])

if __name__ == '__main__':
    unittest.main()
