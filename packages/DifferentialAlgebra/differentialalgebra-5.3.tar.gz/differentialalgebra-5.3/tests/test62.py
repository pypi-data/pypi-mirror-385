# DenefLipshitz (exhibited a bug)

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_62(self):
        xi,q,a = var ('xi,q,a')
        x,y,z = indexedbase ('x,y,z')
        R = DifferentialRing (derivations = [xi], blocks = [[x,y,z],q,'(x,y,z)[oo:-1]',a], parameters = [q,'(x,y,z)[oo:-1]',a], notation='jet')
        eqns = [
            x*y*y[xi,xi] + y[xi] + y**2 + z,
            z[0] - 1,
            x[xi] - 1, x[0]]
        Y = [x,y,z]
        Ybar = { x['(xi,k)'] : 'x[k]',
                 y['(xi,k)'] : 'y[k]',
                 z['(xi,k)'] : 'z[k]' }
        DL = R.DenefLipshitz (eqns, Y, Ybar, q, xi)
        self.assertEqual (len(DL), 6)

if __name__ == '__main__':
    unittest.main()


