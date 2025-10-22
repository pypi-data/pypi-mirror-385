# leading_rank

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_11(self):
        t = var ('t')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [t], blocks = [u,v])
        L = [t, u(t)**2 - u(t), Derivative(v(t),t), 1/v(t)]
        L = R.leading_rank (L)
        self.assertEqual (L, [t, u(t)**2, Derivative(v(t),t), 1/v(t)])
        L = R.leading_rank (L, listform = True)
        self.assertEqual (L, [[t, 1], [u(t), 2], [Derivative(v(t),t), 1], [v(t), -1]])
        L = R.leading_rank (1/u(t)**2)
        self.assertEqual (L, u(t)**(-2))
        L = R.leading_rank (1/u(t)**2, listform = True)
        self.assertEqual (L, [u(t), -2])
        L = R.leading_rank (u(t)**2)
        self.assertEqual (L, u(t)**2)
        L = R.leading_rank (u(t)**2, listform = True)
        self.assertEqual (L, [u(t), 2])
        L = R.leading_rank ((u(t)-1)/(u(t)+2))
        self.assertEqual (L, 1)
        L = R.leading_rank ((u(t)-1)/(u(t)+2), listform = True)
        self.assertEqual (L, [u(t), 0])

if __name__ == '__main__':
    unittest.main()
