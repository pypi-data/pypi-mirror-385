# tail

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_14(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t + 3, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.tail (L)
        self.assertEqual (L, [3, -u(t) + Derivative(v(t),t) + 1, 0])
        eq = u(t)**2 + Derivative(v(t),t)/v(t)
        L = R.tail (eq)
        self.assertEqual (L, Derivative(v(t),t)/v(t))
        L = R.initial (eq) * R.leading_rank (eq) + R.tail (eq) - eq
        self.assertEqual (L, 0)
        L = [t + 3, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.tail (L, t)
        self.assertEqual (L, [3, 0, 0])
        eq = u(t)**2 + Derivative(v(t),t)/v(t)
        derv = Derivative(v(t), t)
        L = R.tail (eq, derv)
        self.assertEqual (L, u(t)**2)
        L = R.leading_coefficient (eq, derv) * derv + R.tail (eq, derv) - eq
        self.assertEqual (L, 0)

if __name__ == '__main__':
    unittest.main()
