# parameters = [w(x)]

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_9(self):
        x,y = var ('x,y')
        w = indexedbase ('w')
        R = DifferentialRing (derivations = [x,y], blocks = [w], parameters = [function('w')(x)], notation = 'jet')
        self.assertEqual (R.normal_form (w[x]), w[x])
        self.assertEqual (R.normal_form (w[y]), 0)

if __name__ == '__main__':
    unittest.main()
