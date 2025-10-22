# factor_derivative

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_07(self):
        a,x,y = var ('a,x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [u,v,a], parameters = [a,v(y)])
        L = R.factor_derivative (Derivative(u(x,y),x))
        self.assertEqual (L, (x, u(x,y)))
        L = R.factor_derivative (a)
        self.assertEqual (L, (1, a))
        derv = Derivative(u(x,y),x,x,y)
        theta, symb = R.factor_derivative (derv)
        self.assertEqual (theta, x**2*y)
        self.assertEqual (symb, u(x,y))
        res = derv - R.differentiate (symb, theta)
        self.assertEqual (res, 0)

if __name__ == '__main__':
    unittest.main()
