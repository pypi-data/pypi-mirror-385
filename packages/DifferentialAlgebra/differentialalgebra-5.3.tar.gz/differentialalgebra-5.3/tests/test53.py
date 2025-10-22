# regchain.RosenfeldGroebner

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_53(self):
        x = var ('x')
        y,z = indexedbase ('y,z')
        R = DifferentialRing (derivations = [x], blocks = [z,y], notation = 'jet')
        ideal = R.RosenfeldGroebner ([y[x]**2 - 4*y])
        C = ideal[0]
        ideal = C.RosenfeldGroebner ([z[x]**2 - y*z])
        L = [ C.equations () for C in ideal ]
        self.assertEqual (L, [[y[x]**2 - 4*y, z[x]**2 - y*z], [y[x]**2 - 4*y, z]])

if __name__ == '__main__':
    unittest.main()

