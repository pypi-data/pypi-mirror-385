# sort and indets

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_05(self):
        x,a,b = var ('x,a,b')
        y,z = function ('y,z')
        R = DifferentialRing (derivations = [x], blocks = [z,y,a,b], parameters = [a,b])
        poly = a*Derivative(y(x),x) + b + x*y(x) + Derivative(z(x),x)**2 + z(x)
        L = R.sort (R.indets (poly, selection = 'all'), 'descending')
        self.assertEqual (L, [Derivative(z(x),x), z(x), Derivative(y(x),x), y(x), a, b, x])

        S = DifferentialRing (derivations = [x], blocks = [b,a,y,z], parameters = [a,b])
        L = S.sort (R.indets (poly, selection = 'all'), 'descending')
        self.assertEqual (L, [b, a, Derivative(y(x),x), y(x), Derivative(z(x),x), z(x), x])

        T = DifferentialRing (derivations = [x], blocks = [[z,y],a,b], parameters = [a,b])
        L = T.sort (R.indets (poly, selection = 'all'), 'descending')
        self.assertEqual (L, [Derivative(z(x),x), Derivative(y(x),x), z(x), y(x), a, b, x])

        x,y = var('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[u,v]], parameters = [v(y)])
        poly = u(x,y) + v(y)
        L = R.sort (R.indets (poly, selection = 'all'), 'descending')
        self.assertEqual (L, [u(x,y), v(y)])

if __name__ == '__main__':
    unittest.main()
