# jet0 notation

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_43(self):
        x = var('x')
        y = indexedbase ('y')
        eta,z = indexedbase ('eta,z')
        R = DifferentialRing (derivations = [x], blocks = [y, eta, z], notation='jet0')
        F = y[0]*y[x]+y[x,x]**2
        self.assertEqual (R.leading_derivative(F), y[x,x])
        self.assertEqual (R.differentiate(F,x), y[0]*y[x, x] + 2*y[x, x, x]*y[x, x] + y[x]**2)
        Z = R.evaluate (F, {y:z+eta})
        self.assertEqual (Z, (eta + z)*(eta[x] + z[x]) + (eta[x, x] + z[x, x])**2)
        Z = R.evaluate (F, {y[0]:z[0]+eta[0]})
        self.assertEqual (Z, (eta[0] + z[0])*(eta[x] + z[x]) + (eta[x, x] + z[x, x])**2)

if __name__ == '__main__':
    unittest.main()
