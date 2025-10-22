# leading_polynomial

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_65(self):
        xi,q,a = var ('xi,q,a')
        x,y,z = indexedbase ('x,y,z')
        R = DifferentialRing (derivations = [xi], blocks = [[x,y,z],q,'(x,y,z)[oo:-1]',a], parameters = [q,'(x,y,z)[oo:-1]',a], notation='jet')
        eqns = [
            x*y*y[xi,xi] + y[xi] + y**2 - 11/Integer(2)*x**2 
                - 1/Integer(8)*x + 1, 2*y[0] + 1, x[xi] - 1, x[0]]
        Y = [x,y]
        Ybar = { x['(xi,k)'] : 'x[k]',
                 y['(xi,k)'] : 'y[k]' }
        DL = R.DenefLipshitz (eqns, Y, Ybar, q)
        U = DL[0]
        poly = U.leading_polynomial ()
        self.assertEqual (y.subs(poly), (q+2, 5, 4))

if __name__ == '__main__':
    unittest.main()


