# BaseFieldExtension

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_37(self):
        x,a,b = var('x,a,b')
        y = function ('y')
        R = DifferentialRing (derivations = [x], blocks = [y,[a,b]], parameters = [a,b])
        F = BaseFieldExtension (generators = [a,b])
        Z = F.generators ()
        self.assertEqual (Z, [a, b])
        Z = F.relations ().equations ()
        self.assertEqual (Z, [])
        F = BaseFieldExtension (generators = [a,b], ring = R)
        L = R.RosenfeldGroebner ([Derivative(y(x),x)**2-a*y(x)], basefield = F)
        Z = [ C.equations () for C in L ]
        self.assertEqual (Z, [[-a*y(x) + Derivative(y(x),x)**2], [y(x)]])
        #
        x,y = var ('x,y')
        f,u = function ('f,u')
        R = DifferentialRing (derivations = [x,y], blocks = [u,f], parameters = [u(x)])
        eqns = [Eq(Derivative(f(x,y),x),f(x,y)**2 + 1), Eq(Derivative(f(x,y),y), 2*y*(f(x,y)**2 + 1))]
        C = RegularDifferentialChain (eqns, R, pretend=False)
        F = BaseFieldExtension (relations = C)
        Z = F.generators ()
        self.assertEqual (Z, [f])
        Z = F.relations ().equations ()
        self.assertEqual (Z, [-2*y*f(x, y)**2 - 2*y + Derivative(f(x, y),y), -f(x, y)**2 + Derivative(f(x, y),x) - 1])
        eqn = Derivative(u(x),x)**2-(f(x,y)**2+1)*u(x)
        L = R.RosenfeldGroebner ([eqn], basefield = F)
        Z = [ C.equations () for C in L ]
        self.assertEqual (Z, [[-2*y*f(x, y)**2 - 2*y + Derivative(f(x, y), y), -f(x, y)**2 + Derivative(f(x, y), x) - 1, -f(x, y)**2*u(x) - u(x) + Derivative(u(x), x)**2], [-2*y*f(x, y)**2 - 2*y + Derivative(f(x, y), y), -f(x, y)**2 + Derivative(f(x, y), x) - 1, u(x)]])

if __name__ == '__main__':
    unittest.main()
