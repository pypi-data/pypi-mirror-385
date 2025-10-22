# __ranking with range indexed groups

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_57(self):
        x,y = var('x,y')
        f,z = indexedbase('f,z')
        R = DifferentialRing(derivations = [x,y], blocks = [f,'(z)[0:oo]'], parameters = ['(z)[0:oo]'], notation = 'jet')
        rnk = R._ranking()
        self.assertEqual (rnk, b"ranking (derivations = [x, y], blocks = [grlexA[f], grlexA['(z)[0:oo]']], parameters = ['(z)[0:oo]'])")
        R = DifferentialRing(derivations = [x,y], blocks = [f,'(z)[0:oo]'], parameters = ['(z)[0:oo](x)'], notation = 'jet')
        rnk = R._ranking()
        self.assertEqual (rnk, b"ranking (derivations = [x, y], blocks = [grlexA[f], grlexA['(z)[0:oo]']], parameters = [sympy.Function('(z)[0:oo]')(x)])")

if __name__ == '__main__':
    unittest.main()
