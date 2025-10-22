# initial

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_12(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t, v(t)*u(t)**2 - u(t) + Derivative(v(t),t) + 1, t*u(t)/Derivative(v(t),t)]
        L = R.initial (L)
        self.assertEqual (L, [1, v(t), t/Derivative(v(t),t)])
        L = R.initial (u(t)**2 + 1/v(t))
        self.assertEqual (L, 1)

if __name__ == '__main__':
    unittest.main()
