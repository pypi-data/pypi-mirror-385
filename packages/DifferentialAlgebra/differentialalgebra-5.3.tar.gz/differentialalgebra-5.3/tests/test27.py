# leading_rank

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_27(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        C = ideal [0]  
        Z = C.leading_rank()
        self.assertEqual (Z, [Derivative (u(x,y),y)**2, Derivative (u(x,y),x)**2, Derivative (v(x,y),y), Derivative (v(x,y),(x,2))])
        Z = C.leading_rank(listform=True)
        self.assertEqual (Z, [[Derivative(u(x, y), y), 2], [Derivative(u(x, y), x), 2], [Derivative(v(x, y), y), 1], [Derivative(v(x, y), (x, 2)), 1]])

if __name__ == '__main__':
    unittest.main()
