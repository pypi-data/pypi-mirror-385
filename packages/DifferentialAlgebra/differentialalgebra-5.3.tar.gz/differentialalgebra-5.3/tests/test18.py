# differential_prem

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_18(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        redset = [eq1, eq2, eq3]
        ideal = R.RosenfeldGroebner (redset)
        C = ideal [0]
        poly = Integer(1)/Integer(7)*u(x,y)
        h, r = R.differential_prem (poly, redset)
        self.assertEqual ((h, r), (1, Integer(1)/Integer(7)*u(x, y)))
        L = C.normal_form (h * poly - r)
        self.assertEqual (L, 0)
        poly = (Integer(1)/Integer(7))*Derivative(v(x,y),x,y) + Derivative(u(x,y),x,x)
        h, r = R.differential_prem (poly, redset)
        zero = R.normal_form (Integer(2)/Integer(7)*(Derivative (v(x,y),x,y) + 14)*Derivative (u(x,y),x) - r)
        self.assertEqual ((h, zero), (2*Derivative (u(x,y),x), 0))
        L = C.normal_form (h * poly - r)
        self.assertEqual (L, 0)
        h, r = R.differential_prem (poly, redset, mode = 'partial')
        zero = R.normal_form (Integer(2)/Integer(7)*(Derivative (v(x,y),x,y) + 14)*Derivative (u(x,y),x) - r)
        self.assertEqual ((h, zero), (2*Derivative (u(x,y),x), 0))
        L = C.normal_form (h * poly - r)
        self.assertEqual (L, 0)
        h, r = R.differential_prem (poly, redset, mode = 'algebraic')
        zero = R.normal_form (Derivative(u(x,y),(x,2)) + Integer(1)/Integer(7)*Derivative (v(x,y),x,y) - r)
        self.assertEqual ((h, zero), (1, 0))
        L = C.normal_form (h * poly - r)
        self.assertEqual (L, 0)

if __name__ == '__main__':
    unittest.main()
