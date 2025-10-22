# BaseFieldExtension, coeffs

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_06(self):
        x,y = var ('x,y')
        f,u = function ('f,u')
        R = DifferentialRing (derivations = [x,y], blocks = [u,f], parameters = [u(x)])
        eqns = [Eq (Derivative(f(x,y),x),f(x,y)**2 + 1), Eq(Derivative(f(x,y),y),2*y*(f(x,y)**2 + 1))]
        C = RegularDifferentialChain (eqns, R, pretend=False)
        F = BaseFieldExtension (relations = C)
        eqn = x*Derivative(u(x),x)**2-(f(x,y)**2+1)*u(x)
        L = R.coeffs (eqn)
        self.assertEqual (L, ([1, -1, -1], [x*Derivative(u(x),x)**2,f(x,y)**2*u(x),u(x)]))
        L = R.coeffs (eqn, Derivative(f(x,y),x))
        self.assertEqual (L, ([x, -f(x,y)**2-1], [Derivative(u(x),x)**2,u(x)]))
        L = R.coeffs (eqn, basefield = F)
        self.assertEqual (L, ([x, -f(x,y)**2-1], [Derivative(u(x),x)**2,u(x)]))
        L = R.coeffs (eqn, basefield = BaseFieldExtension ())
        self.assertEqual (L, ([x, -1, -1], [Derivative(u(x), x)**2, f(x, y)**2*u(x), u(x)]))
        
        eqn = x*Derivative(u(x),x)**2-u(x)/Derivative(f(x,y),x)
        L = R.coeffs (eqn)
        self.assertEqual (L, ([1, -1], [x*Derivative(u(x), x)**2, u(x)/Derivative(f(x, y), x)]))
        L = R.coeffs (eqn, basefield = F)
        self.assertEqual (L, ([x, -1/Derivative(f(x, y), x)], [Derivative(u(x), x)**2, u(x)]))
        L = R.coeffs (eqn, basefield = BaseFieldExtension ()) 
        self.assertEqual (L, ([x, -1], [Derivative(u(x), x)**2, u(x)/Derivative(f(x, y), x)]))

if __name__ == '__main__':
    unittest.main()
