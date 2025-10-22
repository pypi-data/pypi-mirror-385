# jet(-1) notation

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_44(self):
        x = var('x')
        y = indexedbase ('y')
        eta,z = indexedbase ('eta,z')
        R = DifferentialRing (derivations = [x], blocks = [y, eta, z], notation='jet(-1)')
        F = y*y[x]+y[x,x]**2
        self.assertEqual (R.leading_derivative(F), y[x,x])
        self.assertEqual (R.differentiate(F,x), y[-1]*y[x, x] + 2*y[x, x, x]*y[x, x] + y[x]**2)

if __name__ == '__main__':
    unittest.main()
