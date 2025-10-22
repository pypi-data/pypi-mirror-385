# jet(_) notation

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_45(self):
        x = var('x')
        y = indexedbase ('y')
        eta,z = indexedbase ('eta,z')
        R = DifferentialRing (derivations = [x], blocks = [y, eta, z], notation='jet(_)')
        F = y*y[x]+y[x,x]**2
        G = R.normal_form (F)
        self.assertEqual (R.leading_derivative(F), y[x,x])
        self.assertEqual (R.leading_derivative(G), y[x,x])
        _ = var('_')
        self.assertEqual (R.differentiate(F,x), y[_]*y[x, x] + 2*y[x, x, x]*y[x, x] + y[x]**2)
        self.assertEqual (R.differentiate(G,x), y[_]*y[x, x] + 2*y[x, x, x]*y[x, x] + y[x]**2)

if __name__ == '__main__':
    unittest.main()
