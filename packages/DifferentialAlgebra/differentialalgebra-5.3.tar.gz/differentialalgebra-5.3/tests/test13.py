# leading_coefficient

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_13(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.leading_coefficient (L)
        self.assertEqual (L, [1, v(t), t/Derivative(v(t),t)])
        L = R.leading_coefficient (u(t)**2 + 1/v(t))
        self.assertEqual (L, 1)
        L = [t, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.leading_coefficient (L, t)
        self.assertEqual (L, [1, u(t)**2*v(t) - u(t) + Derivative(v(t),t) + 1, u(t)/Derivative(v(t),t)])
        L = R.leading_coefficient (u(t)**2 + Derivative(v(t),t)/v(t), Derivative(v(t),t))
        self.assertEqual (L, 1/v(t))

if __name__ == '__main__':
    unittest.main()
