# evaluate

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_38(self):
        D = var('D')
        x = var('x')
        y = indexedbase('y')
        R = DifferentialRing (derivations = [x], blocks = [y,D], parameters = [D], notation='jet')
        P = y*y[x]**2 + y - D
        ybar = Add (*[y[i]*x**i for i in range (5)]).subs({y[0]:2, y[1]:0})
        evdict = {}
        evdict[y] = ybar
        evdict[D] = 2
        serie = collect (expand (R.evaluate (P, evdict).doit()), x)
        Z = rem (serie, x**3, x)
        self.assertEqual (Z, x**2*(8*y[2]**2 + y[2]))
        t = var('t')
        R = DifferentialRing (derivations = [x,t], blocks = [y,D], parameters = [D], notation='jet')
        serie = collect (expand (R.evaluate (P, evdict).doit()), x)
        Z = rem (serie, x**3, x)
        self.assertEqual (Z, x**2*(8*y[2]**2 + y[2]))
        serie = collect (expand (R.evaluate (y[t], evdict).doit()), x)
        self.assertEqual (serie, 0)

if __name__ == '__main__':
    unittest.main()
