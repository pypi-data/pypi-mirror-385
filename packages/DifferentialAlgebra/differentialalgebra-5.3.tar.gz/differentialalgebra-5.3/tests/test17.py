# differentiate

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_17(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        eq = u(t)**2
        L = R.differentiate (eq)
        self.assertEqual (L, u(t)**2)
        L = R.differentiate (eq, 1)
        self.assertEqual (L, u(t)**2)
        L = R.differentiate (eq, t)
        self.assertEqual (L, 2*u(t)*Derivative(u(t),t))
        L = R.differentiate (eq, t, t)
        self.assertEqual (L, 2*u(t)*Derivative(u(t),(t,2)) + 2*Derivative(u(t),t)**2)
        L = R.differentiate (eq, t**2) 
        self.assertEqual (L, 2*u(t)*Derivative(u(t),(t,2)) + 2*Derivative(u(t),t)**2)
        L = R.differentiate (eq, t**2, t)
        self.assertEqual (L, 2*u(t)*Derivative(u(t),(t,3)) + 6*Derivative(u(t),t)*Derivative(u(t),(t,2)))

if __name__ == '__main__':
    unittest.main()
