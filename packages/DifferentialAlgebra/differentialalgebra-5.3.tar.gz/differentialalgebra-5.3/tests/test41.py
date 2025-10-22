# is_differential_fraction

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_41(self):
        x = var('x')
        w = function('y')
        R = DifferentialRing (derivations = [x], blocks = [w])
        F = w(x) + Derivative(w(x),x) + 1
        self.assertTrue (R.is_differential_fraction ([F, 1/F]))
        self.assertTrue (R.is_differential_fraction(1/x))
        self.assertTrue (R.is_differential_fraction(x**(-3)))
        self.assertFalse (R.is_differential_fraction(x**(Rational(3,4))))
        self.assertFalse (R.is_differential_fraction(var('t')))

if __name__ == '__main__':
    unittest.main()
