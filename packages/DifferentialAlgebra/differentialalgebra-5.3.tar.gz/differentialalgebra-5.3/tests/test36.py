# preparation_congruence

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_36(self):
        t = var('t')
        u = function('u')
        R = DifferentialRing (derivations = [t], blocks = [u])
        poly = Derivative(u(t),t)**2 - 4*u(t)
        ideal = R.RosenfeldGroebner ([poly])
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(Derivative(u(t), t)**2, 4*u(t))], [Eq(u(t), 0)]])
        C = ideal [1]
        Z = C.preparation_equation (poly)
        z1 = function('z1')
        self.assertEqual (Z, Eq(Derivative(u(t),t)**2 - 4*u(t), Derivative(z1(t),t)**2 - 4*z1(t)))
        Z = C.preparation_equation (poly, congruence=True)
        self.assertEqual (Z, Eq(Derivative(u(t),t)**2 - 4*u(t), - 4*z1(t)))
        ideal = R.RosenfeldGroebner ([poly], singsol = 'essential')
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(Derivative(u(t), t)**2, 4*u(t))], [Eq(u(t), 0)]])
        poly = Derivative(u(t),t)**2 - 4*u(t)**3
        ideal = R.RosenfeldGroebner ([poly])
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(Derivative(u(t), t)**2, 4*u(t)**3)], [Eq(u(t), 0)]])
        C = ideal [1]
        Z = C.preparation_equation (poly)
        self.assertEqual (Z, Eq(-4*u(t)**3 + Derivative(u(t), t)**2, -4*z1(t)**3 + Derivative(z1(t), t)**2))
        Z = C.preparation_equation (poly, congruence = True)
        self.assertEqual (Z, Eq(-4*u(t)**3 + Derivative(u(t), t)**2, Derivative(z1(t), t)**2))
        ideal = R.RosenfeldGroebner ([poly], singsol = 'essential')
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(Derivative(u(t), t)**2, 4*u(t)**3)]])
        t = var('t')
        u,s,c = function ('u,s,c')
        R = DifferentialRing (derivations = [t], blocks = [u,[s,c]])
        C = RegularDifferentialChain ([Derivative(c(t),t) + s(t), s(t)**2 + c(t)**2 - 1], R)
        F = BaseFieldExtension (relations = C)
        poly = Derivative(u(t),t)**2 - 4*u(t)**3
        poly2 = Derivative(u(t),t)**2 - 4*u(t)**3 + s(t)**2 + c(t)**2 - 1
        ideal = R.RosenfeldGroebner ([poly], basefield = F)
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(s(t)**2, 1 - c(t)**2), Eq(Derivative(c(t), t), -s(t)), Eq(Derivative(u(t), t)**2, 4*u(t)**3)], [Eq(s(t)**2, 1 - c(t)**2), Eq(Derivative(c(t), t), -s(t)), Eq(u(t), 0)]])
        C = ideal[1]
        Z = C.equations (solved = True)
        self.assertEqual (Z, [Eq(s(t)**2, 1 - c(t)**2), Eq(Derivative(c(t), t), -s(t)), Eq(u(t), 0)])
        C3 = function('C3')
        Z = C.preparation_equation (poly, zstring = 'C%d')
        self.assertEqual (Z, Eq(-4*u(t)**3 + Derivative(u(t), t)**2, -4*C3(t)**3 + Derivative(C3(t), t)**2))
        Z = C.preparation_equation (poly, congruence=True)
        z3 = function('z3')
        self.assertEqual (Z, Eq(-4*u(t)**3 + Derivative(u(t), t)**2, Derivative(z3(t), t)**2))
        Z = C.preparation_equation (poly2)
        self.assertEqual (Z, Eq(c(t)**2 + s(t)**2 - 4*u(t)**3 + Derivative(u(t), t)**2 - 1, z1(t) - 4*z3(t)**3 + Derivative(z3(t), t)**2))
        Z = C.preparation_equation (poly2, congruence=True)
        self.assertEqual (Z, Eq(c(t)**2 + s(t)**2 - 4*u(t)**3 + Derivative(u(t), t)**2 - 1, z1(t)))
        Z = C.preparation_equation (poly2, congruence=True, basefield=F)
        self.assertEqual (Z, Eq(c(t)**2 + s(t)**2 - 4*u(t)**3 + Derivative(u(t), t)**2 - 1, Derivative(z3(t), t)**2))
        ideal = R.RosenfeldGroebner ([poly], singsol = 'essential', basefield = F)
        Z = [ C.equations (solved = True) for C in ideal ]
        self.assertEqual (Z, [[Eq(s(t)**2, 1 - c(t)**2), Eq(Derivative(c(t), t), -s(t)), Eq(Derivative(u(t), t)**2, 4*u(t)**3)]])

if __name__ == '__main__':
    unittest.main()
