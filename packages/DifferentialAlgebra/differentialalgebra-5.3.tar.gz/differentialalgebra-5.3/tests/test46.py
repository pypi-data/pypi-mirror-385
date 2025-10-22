# y[i] for i in range (10)

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_46(self):
        y = indexedbase ('y')
        R = DifferentialRing (derivations = [], blocks = [y[i] for i in range(10)], notation='jet')
        F = y[5]*y[4]+y[3]**2-1
        G = R.normal_form (F)
        self.assertEqual (R.leading_derivative(F), y[3])
        self.assertEqual (G, F)

if __name__ == '__main__':
    unittest.main()
