# integrate

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_16(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [[u,v]])
        eq = Derivative(u(t),t)**2 + Derivative(v(t)**2,t,t) - Derivative(u(t)*v(t) + t*v(t), t)
        eq = eq.doit ()
        L = R.integrate (eq, t)
        self.assertEqual (L, [Derivative(u(t),t)**2, -t*v(t) - u(t)*v(t), v(t)**2])
        zero = eq - sum ([R.differentiate (L[i], t**i) for i in range (len (L))])
        self.assertEqual (zero, 0)
        eq = (v(t)**2 + t)/(3*Derivative(v(t),t))              
        L = R.integrate (Derivative(eq, t).doit (), t)
        self.assertEqual (L, [0, (v(t)**2 + t)/(3*Derivative(v(t),t))])
        zero = L[1] - eq
        self.assertEqual (zero, 0)

if __name__ == '__main__':
    unittest.main()
