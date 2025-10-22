# separant

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_15(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t + 3, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.separant (L)
        self.assertEqual (L, [1, 2*u(t)*v(t) - 1, t/Derivative(v(t),t)])
        L = R.separant (u(t)**2 + Derivative(v(t),t)/v(t))
        self.assertEqual (L, 2*u(t))
        L = [t + 3, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.separant (L, t)
        self.assertEqual (L, [1, 0, u(t)/Derivative(v(t),t)])
        L = R.separant (u(t)**2 + Derivative(v(t),t)/v(t), Derivative(v(t),t))
        self.assertEqual (L, 1/v(t))

if __name__ == '__main__':
    unittest.main()
