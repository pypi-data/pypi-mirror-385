# DenefLipshitz

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_60(self):
        x,q = var ('x,q')
        y = indexedbase ('y')
        R = DifferentialRing (blocks = [y,q,'(y)[oo:-1]'], derivations = [x], parameters = [q,'(y)[oo:-1]'], notation = 'jet')
        eqns = [ y*y[x]**2 + y - 1, 2*y[0] - 1 ]
        Y = [y]
        Ybar = { y['(x,k)'] : 'y[k]' } 
        DL = R.DenefLipshitz (eqns, Y, Ybar, q, x)
        self.assertEqual (len(DL), 1)

if __name__ == '__main__':
    unittest.main()


