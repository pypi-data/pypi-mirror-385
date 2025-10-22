# change_ranking

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_34(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        C = ideal [0]  
        Z = C.equations (solved = True)
        self.assertEqual (Z, [Eq(Derivative(u(x, y), y)**2, 2*u(x, y)), Eq(Derivative(u(x, y), x)**2, 4*u(x, y)), Eq(Derivative(v(x, y), y), (u(x, y)*Derivative(u(x, y), x)*Derivative(u(x, y), y) - Derivative(u(x, y), x)*Derivative(u(x, y), y))/(4*u(x, y))), Eq(Derivative(v(x, y), (x, 2)), Derivative(u(x, y), x))])
        Rbar = DifferentialRing (derivations = [x,y], blocks = [u,v])
        Cbar = C.change_ranking (Rbar, prime=True)
        Z = Cbar.equations (solved = True)
        self.assertEqual (Z, [Eq(Derivative(v(x, y), (y, 2))**4, 2*Derivative(v(x, y), y)**2 + 2*Derivative(v(x, y), (y, 2))**2 - 1), Eq(Derivative(v(x, y), x, y), (Derivative(v(x, y), (y, 2))**3 - Derivative(v(x, y), (y, 2)))/Derivative(v(x, y), y)), Eq(Derivative(v(x, y), (x, 2)), 2*Derivative(v(x, y), (y, 2))), Eq(u(x, y), Derivative(v(x, y), (y, 2))**2)])

if __name__ == '__main__':
    unittest.main()
