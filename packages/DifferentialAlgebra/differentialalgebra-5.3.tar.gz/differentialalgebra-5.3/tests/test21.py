# RosenfeldGroebner
# test to be completed

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_21(self):
        x = var('x')
        y = function ('y')
        R = DifferentialRing (derivations = [x], blocks = [y])
        L = R.RosenfeldGroebner ([Derivative(y(x),x)**2-4*y(x)], singsol = 'essential')
        self.assertEqual (L[0].equations (), [Derivative(y(x),x)**2 - 4*y(x)])
        self.assertEqual (L[1].equations (), [y(x)])
        x,y = var('x,y')
        u,v = function('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(Derivative(u(x,y),x),y) * Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(Derivative(v(x,y),x),x) - Derivative(u(x,y),x)
        L = R.RosenfeldGroebner ([eq1, eq2, eq3])
        Z = L[0].equations (solved=True)
        self.assertEqual (Z, [Eq(Derivative(u(x, y), y)**2, 2*u(x, y)), Eq(Derivative(u(x, y), x)**2, 4*u(x, y)), Eq(Derivative(v(x, y), y), (u(x, y)*Derivative(u(x, y), x)*Derivative(u(x, y), y) - Derivative(u(x, y), x)*Derivative(u(x, y), y))/(4*u(x, y))), Eq(Derivative(v(x, y), (x, 2)), Derivative(u(x, y), x))])

if __name__ == '__main__':
    unittest.main()
