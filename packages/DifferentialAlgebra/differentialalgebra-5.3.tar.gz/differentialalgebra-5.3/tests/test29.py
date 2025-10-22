# leading_coefficient

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_29(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        C = ideal [0]  
        Z = C.leading_coefficient()
        self.assertEqual (Z, [1, 1, 4*u(x,y), 1])
        Z = C.leading_coefficient(u(x,y))
        self.assertEqual (Z, [-2, -4, -Derivative (u(x,y),x)*Derivative (u(x,y),y) + 4*Derivative (v(x,y),y), -Derivative (u(x,y),x) + Derivative (v(x,y),(x,2))])

if __name__ == '__main__':
    unittest.main()
