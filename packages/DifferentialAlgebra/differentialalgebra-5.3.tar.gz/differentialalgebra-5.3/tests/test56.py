# parameters defined by range indexed groups

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_56(self):
        x,y = var('x,y')
        f,z = indexedbase('f,z')
        R = DifferentialRing(derivations = [x,y], blocks = [f,'(z)[0:oo]'], parameters = ['(z)[0:oo]'], notation = 'jet')
        p = f + x*z[3]
        q = R.differentiate(p, x)
        self.assertEqual (q, f[x] + z[3])
        R = DifferentialRing(derivations = [x,y], blocks = [f,z,'(z)[0:oo]'], parameters = ['(z)[0:oo]'], notation = 'jet')
        p = f + x*z[3] + z
        q = R.differentiate(p, x, x)
        self.assertEqual (q, f[x,x] + z[x,x])

if __name__ == '__main__':
    unittest.main()
