# evaluate

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_40(self):
        x = var('x')
        w = function('y')
        R = DifferentialRing (derivations = [x], blocks = [w])
        F = w(x) + Derivative(w(x),x) + 1
        series = R.evaluate (F, {w:x**3})
        self.assertEqual (series.doit (), x**3 + 3*x**2 + 1)

if __name__ == '__main__':
    unittest.main()
