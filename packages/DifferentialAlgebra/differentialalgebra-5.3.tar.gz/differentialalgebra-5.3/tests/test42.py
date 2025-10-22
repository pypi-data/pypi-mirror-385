# evaluate

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_42(self):
        x = var('x')
        y = indexedbase ('y')
        eta,z = indexedbase ('eta,z')
        blks = [y, z, eta]
        R = DifferentialRing (derivations = [x], blocks = blks, notation='jet')
        F = y*y[x]+y[x,x]**2
        Z = R.evaluate (F, {y:z+eta})
        self.assertEqual (Z, (eta[x,x] + z[x,x])**2 + (eta[x] + z[x])*(eta + z))

if __name__ == '__main__':
    unittest.main()
