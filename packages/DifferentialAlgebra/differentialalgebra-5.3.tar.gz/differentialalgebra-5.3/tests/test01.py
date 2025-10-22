# Ritt's famous example

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_01(self):
        x = symbols('x')
        y = Function ('y')
        eq = Derivative(y(x),x)**2-4*y(x)
        R = DifferentialRing (derivations = [x], blocks = [y])
        ideal = R.RosenfeldGroebner([eq])
        C = ideal [0]
        self.assertEqual (C.equations (), [eq])

if __name__ == '__main__':
    unittest.main()

