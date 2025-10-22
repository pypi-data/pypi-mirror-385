# equations

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_22(self):
        x,y = var('x,y')
        w,z,a = function ('w,z,a') 
        R = DifferentialRing (derivations = [x,y], blocks = [[w,a],z], parameters = [a(y)]) 
        L = [0, 18, a(y)**2, Derivative(a(y),y), w(x,y) - z(x,y)]
        leader,order,rank = var('leader,order,rank')
        derivative,proper = function('derivative,proper')
        self.assertEqual (R.equations (L), [0, 18, a(y)**2, Derivative(a(y),y), -z(x, y) + w(x, y)])
        self.assertEqual (R.equations (L, selection = Eq(rank,0)), [0])
        self.assertEqual (R.equations (L, selection = Eq(rank,1)), [18])
        Z = R.equations (L, solved = True, selection = rank > 1)
        self.assertEqual (Z, [Eq(a(y)**2,0), Eq(Derivative(a(y),y),0), Eq(w(x, y),z(x, y))])
        Z = R.equations (L, selection = Eq(leader,derivative (a(y))))
        self.assertEqual (Z, [a(y)**2, Derivative(a(y),y)])
        Z = R.equations (L, solved = True, selection = Eq(leader,derivative (w(x,y))))
        self.assertEqual (Z, [Eq(w(x, y),z(x, y))] )
        Z = R.equations (w(x,y) - a(y), solved=True)
        self.assertEqual (Z, Eq(w(x, y),a(y)))

if __name__ == '__main__':
    unittest.main()
