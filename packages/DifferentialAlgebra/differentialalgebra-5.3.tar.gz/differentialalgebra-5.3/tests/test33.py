# differential_prem

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_33(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        C = ideal [0]  
        C.equations (solved = True)
        poly = (Integer(1)/Integer(7))*u(x,y)
        h, r = C.differential_prem (poly)
        self.assertEqual ((h, r), (1, u(x,y)/7))
        Z = C.normal_form (h * poly - r)
        self.assertEqual (Z, 0)
        poly = (Integer(1)/Integer(7))*Derivative(v(x,y),x,y) + Derivative(u(x,y),x,x)
        h, r = C.differential_prem (poly)
        self.assertEqual ((16*u(x, y)**2*Derivative(u(x, y), x)*Derivative(u(x, y), y) - h).expand(), 0)
        self.assertEqual ((32*(u(x, y) + 7*Derivative(u(x, y), y))*u(x, y)**2*Derivative(u(x, y), x)/7 - r).expand(), 0)
        Z = C.normal_form (h * poly - r)
        self.assertEqual (Z, 0)
        h, r = C.differential_prem (poly, mode = 'partial')
        self.assertEqual ((16*u(x, y)*Derivative(u(x, y), x)*Derivative(u(x, y), y) - h).expand(), 0)
        self.assertEqual ((-4*(-u(x, y)*Derivative(u(x, y), x)**2 - 2*u(x, y)*Derivative(u(x, y), y)**2 - 56*u(x, y)*Derivative(u(x, y), y) - Derivative(u(x, y), x)**2*Derivative(u(x, y), y)**2 + Derivative(u(x, y), x)**2 + 4*Derivative(u(x, y), x)*Derivative(u(x, y), y)*Derivative(v(x, y), y) + 2*Derivative(u(x, y), y)**2)*Derivative(u(x, y), x)/7 - r).expand(), 0)
        Z = C.normal_form (h * poly - r)
        self.assertEqual (Z, 0)
        h, r = C.differential_prem (poly, mode = 'algebraic')
        self.assertEqual ((h,r), (1, Derivative (u(x,y),(x,2)) + Derivative (v(x,y),x,y)/7))
        Z = C.normal_form (h * poly - r)
        self.assertEqual (Z, 0)

if __name__ == '__main__':
    unittest.main()
