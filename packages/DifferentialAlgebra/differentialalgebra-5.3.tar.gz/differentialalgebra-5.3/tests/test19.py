# normal_form
# test to be improved

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_19(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        eq = R.differentiate(u(t) + (v(t)**2 + t)/(3*u(t)+Derivative(v(t),t)), t)
        L = R.integrate (eq, t)
        zero = eq - R.differentiate(L[1], t)  
        self.assertEqual (R.normal_form (zero), 0)

if __name__ == '__main__':
    unittest.main()
