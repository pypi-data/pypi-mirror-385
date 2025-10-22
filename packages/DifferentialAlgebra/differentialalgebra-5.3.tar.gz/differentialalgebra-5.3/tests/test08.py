# indets / selection

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_08(self):
        x,y,z,t = var ('x,y,z,t')
        u,v,w = function ('u,v,w')
        R = DifferentialRing (derivations = [x,y,t], blocks = [u,[v,w],z], parameters = [u(t,y,x),z,w(y)])
        L = R.indets ()
        self.assertEqual (L, [u(t, y, x), v(x, y, t), w(y), z])
        L = R.indets (selection = 'dependent')
        self.assertEqual (L, [u(t, y, x), v(x, y, t), w(y), z])
        L = R.indets (selection = 'derivatives')
        self.assertEqual (L, [u(t, y, x), v(x, y, t), w(y), z])
        L = R.indets (selection = 'derivations')
        self.assertEqual (L, [x, y, t])
        L = R.indets (selection = 'independent')
        self.assertEqual (L, [x, y, t])
        L = R.indets (selection = 'parameters')
        self.assertEqual (L, [u(t, y, x), w(y), z])
        L = R.indets (selection = 'all')
        self.assertEqual (L, [x, y, t, u(t, y, x), v(x, y, t), w(y), z])
        L = R.indets (selection = 'constants')
        self.assertEqual (L, [z])
        L = R.indets (selection = 'constants', derivation = y)
        self.assertEqual (L, [z])
        L = R.indets (selection = 'constants', derivation = t)
        self.assertEqual (L, [w(y), z])
        eq = u(t,y,x) + 1/w(y)
        L = R.indets (eq)
        self.assertEqual (L, [u(t, y, x), w(y)])
        L = R.indets (eq, selection = 'constants', derivation = x)
        self.assertEqual (L, [w(y)])

if __name__ == '__main__':
    unittest.main()
