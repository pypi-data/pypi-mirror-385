# resultant

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_54(self):
        x = var('x')
        v,u = indexedbase ('v,u')
        R = DifferentialRing (derivations = [x], blocks = [v,u], notation = 'jet')
        A = RegularDifferentialChain ([(u+1)*(v[x]**2 - 4*v)*(v[x] - 2), u[x]**2 - 4*u], R, attributes = ['prime', 'autoreduced']) 
        P = v[x,x] - 2
        S = A.resultant (P)
        self.assertEqual (S, (v[x,x] - 2)**6)
        P = v[x,x] - 2/Integer(3)
        S = A.resultant (P)
        self.assertEqual (S, (3*v[x,x] - 2)**6/3**6)
        A = RegularDifferentialChain ([(u+1)*(v[x]**2 - 4*v)*(v[x] - 2), u[x]**2 - 4*u], R, attributes = ['prime', 'autoreduced', 'differential'])
        P = v[x,x] - 2
        S = A.resultant (P)
        self.assertEqual (S, 0)

if __name__ == '__main__':
    unittest.main()
