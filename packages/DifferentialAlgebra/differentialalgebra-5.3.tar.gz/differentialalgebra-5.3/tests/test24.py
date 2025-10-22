# equations

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_24(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2-4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y)-u(x,y)+1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        eqns = [-2*u(x, y) + Derivative(u(x, y), y)**2, -4*u(x, y) + Derivative(u(x, y), x)**2, -u(x, y)*Derivative(u(x, y), x)*Derivative(u(x, y), y) + 4*u(x, y)*Derivative(v(x, y), y) + Derivative(u(x, y), x)*Derivative(u(x, y), y), -Derivative(u(x, y), x) + Derivative(v(x, y), (x, 2))]
        C = ideal[0]
        leader,rank,order = var ('leader,rank,order')
        derivative,proper = function ('derivative,proper')
        Z = C.equations (solved=True,selection=Eq(rank,Derivative(u(x,y),y)**2))
        self.assertEqual (Z, [Eq(Derivative(u(x, y), y)**2, 2*u(x, y))])
        Z = C.equations (selection = order > 0)
        self.assertEqual (Z, eqns)
        Z = C.equations (selection = Eq(leader,Derivative(u(x,y),x)))
        self.assertEqual (Z, [-4*u(x, y) + Derivative(u(x, y), x)**2])
        Z = C.equations (selection = Eq(leader,derivative (Derivative(u(x,y),x))))
        self.assertEqual (Z, [-4*u(x, y) + Derivative(u(x, y), x)**2])
        Z = C.equations (selection = Eq(leader,proper(Derivative(u(x,y),x))))
        self.assertEqual (Z, [])

if __name__ == '__main__':
    unittest.main()
