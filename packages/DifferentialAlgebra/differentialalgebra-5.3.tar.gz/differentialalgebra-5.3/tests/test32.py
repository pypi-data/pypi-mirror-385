# indets

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_32(self):
        x,y = var ('x,y')
        u,v = function ('u,v')
        R = DifferentialRing (derivations = [x,y], blocks = [[v,u]])
        eq1 = Derivative(u(x,y),x)**2 - 4*u(x,y)
        eq2 = Derivative(u(x,y),x,y)*Derivative(v(x,y),y) - u(x,y) + 1
        eq3 = Derivative(v(x,y),x,x) - Derivative(u(x,y),x)
        ideal = R.RosenfeldGroebner ([eq1,eq2,eq3])
        C = ideal [0]  
        Z = C.indets ()
        self.assertEqual (Z, [u(x, y), Derivative (u(x,y),x), Derivative (v(x,y),y), Derivative (v(x,y),(x,2)), Derivative (u(x,y),y)])
        Z = C.indets (selection = 'derivatives')
        self.assertEqual (Z, [u(x, y), Derivative (u(x,y),x), Derivative (v(x,y),y), Derivative (v(x,y),(x,2)), Derivative (u(x,y),y)])
        Z = C.indets (selection = 'dependent')
        self.assertEqual (Z, [v(x, y), u(x, y)])
        Z = C.indets (selection = 'independent')
        self.assertEqual (Z, [])
        Z = C.indets (selection = 'parameters')
        self.assertEqual (Z, [])
        Z = C.indets (selection = 'all')
        self.assertEqual (Z, [u(x, y), Derivative (u(x,y),x), Derivative (v(x,y),y), Derivative (v(x,y),(x,2)), Derivative (u(x,y),y)])

if __name__ == '__main__':
    unittest.main()
