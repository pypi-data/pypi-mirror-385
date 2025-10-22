# sort

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_20(self):
        a,x,y = var ('a,x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [u,v,a], parameters = [a,v(y)])
        L = [Derivative(v(y),y,y), Derivative(v(y),y,y)**3, 0, a*u(x,y)**2, x]
        Z = R.sort (L)
        self.assertEqual (Z, [0, x, Derivative(v(y),(y,2)), Derivative(v(y),(y,2))**3, a*u(x, y)**2])
        Z = R.sort (L, 'ascending')
        self.assertEqual (Z, [0, x, Derivative(v(y),(y,2)), Derivative(v(y),(y,2))**3, a*u(x, y)**2])
        Z = R.sort (L, 'descending')
        self.assertEqual (Z, [a*u(x, y)**2, Derivative(v(y),(y,2))**3, Derivative(v(y),(y,2)), x, 0])
        L = [ u(x,y), u(x,y)*v(y), u(x,y)*v(y)**2, u(x,y)*v(y)*a ]
        Z = R.sort (L, 'ascending')
        self.assertEqual (Z, [u(x, y), u(x, y)*v(y), a*u(x, y)*v(y), u(x, y)*v(y)**2])
        Z = R.sort (L, 'descending')
        self.assertEqual (Z, [u(x, y)*v(y)**2, a*u(x, y)*v(y), u(x, y)*v(y), u(x, y)])

if __name__ == '__main__':
    unittest.main()
