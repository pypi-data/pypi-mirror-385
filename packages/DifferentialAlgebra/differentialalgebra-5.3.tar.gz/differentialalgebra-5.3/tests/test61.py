# DenefLipshitz

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_61(self):
        x,q = var ('x,q')
        y = indexedbase ('y')
        R = DifferentialRing (blocks = [y,q,'(y)[oo:-1]'], derivations = [x], parameters = [q,'(y)[oo:-1]'], notation = 'jet')
        eqns = [ y*y[x]**2 + y - 1 ]
        Y = [y]
        Ybar = { y['(x,k)'] : 'y[k]' }
        DL = R.DenefLipshitz (eqns, Y, Ybar, q, x)
        U = DL[1]
        V = U.DenefLipshitz ([2*y[0]-1])
        self.assertEqual (len(V), 1)

if __name__ == '__main__':
    unittest.main()


