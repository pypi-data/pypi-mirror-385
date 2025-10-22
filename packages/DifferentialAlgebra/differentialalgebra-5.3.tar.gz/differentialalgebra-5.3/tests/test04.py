# Computation of an integral form of an input-output equation

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_04(self):
        leader,order,rank = var ('leader,order,rank')
        k12, k21, ke, Ve, t = var ('k_12, k_21, k_e, V_e, t')
        x1,x2 = function ('x1,x2')
        params = [ke,Ve,k_12,k_21]
        R = DifferentialRing (derivations = [t], blocks = [[x1,x2], params], parameters = params)
        edoA = Eq(Derivative(x1(t),t), -k12*x1(t) + k21*x2(t) - (Ve*x1(t))/(ke + x1(t)))
        edoB = Eq (Derivative(x2(t),t), k12*x1(t) - k21*x2(t))
        F = BaseFieldExtension (generators = params)
        ideal = R.RosenfeldGroebner ([edoA, edoB], basefield = F)
        C = ideal[0]
        IO_R = DifferentialRing (derivations = [t], blocks = [x2,x1,params], parameters = params)
        IO_C = C.change_ranking (IO_R)
        IO_rel = IO_C.equations ()[0]
        IO_rel = IO_rel / IO_R.initial (IO_rel)
        L = IO_R.integrate (IO_rel, t)
        zero = sum ([ IO_R.differentiate(L[i], t**i) for i in range (0,len(L)) ]) - IO_rel
        self.assertEqual (IO_R.normal_form(zero),0)

if __name__ == '__main__':
    unittest.main()
