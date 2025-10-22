# constraints

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_63(self):
        x,q = var ('x,q')
        y = indexedbase ('y')
        R = DifferentialRing (derivations = [x], blocks = [y,q,'(y)[oo:-1]'], parameters = [q,'(y)[oo:-1]'], notation='jet')
        eqns = [ y*y[x]**2 + y - 1 ]
        Y = [y]
        Ybar = { y['(x,k)'] : 'y[k]' }
        DL = R.DenefLipshitz (eqns, Y, Ybar, q, x)
        self.assertEqual (len(DL), 3)
        L = [ U.constraints () for U in DL ]
        self.assertEqual (len(L), 3)

if __name__ == '__main__':
    unittest.main()


