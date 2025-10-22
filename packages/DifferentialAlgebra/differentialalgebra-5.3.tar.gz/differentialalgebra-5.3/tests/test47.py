# a[x] and z[x,y] - z[y,x]

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_47(self):
        x,y = var('x,y')
        a,z = indexedbase ('a,z')
        R = DifferentialRing (derivations = [x,y], blocks = [z,a], parameters = [a], notation = 'jet')
        p = a[x]
        self.assertEqual (R.normal_form (p), 0)
        p = z[x,y] - z[y,x]
        self.assertEqual (R.normal_form (p), 0)

if __name__ == '__main__':
    unittest.main()
