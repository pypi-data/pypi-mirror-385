# leading_derivative

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_10(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t, u(t)**2 - u(t), Derivative(v(t),t), 1/v(t)]
        L = R.leading_derivative (L)
        self.assertEqual (L, [t, u(t), Derivative(v(t),t), v(t)])
        self.assertEqual (u(t), R.leading_derivative (1/u(t)**2))
        self.assertEqual (u(t), R.leading_derivative (u(t)**2))

if __name__ == '__main__':
    unittest.main()
