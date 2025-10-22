# is_constant

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_09(self):
        a,x,y = var ('a,x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [u,v,a], parameters = [a,v(y)])
        self.assertTrue (R.is_constant (3))
        L = R.is_constant ([1/a,v(y),Derivative(u(x,y),x)/(a+1)])
        self.assertEqual (L, [True, False, False])
        L = R.is_constant ([1/a,v(y),Derivative(u(x,y),x)/(a+1)], x)
        self.assertEqual (L, [True, True, False])

if __name__ == '__main__':
    unittest.main()
