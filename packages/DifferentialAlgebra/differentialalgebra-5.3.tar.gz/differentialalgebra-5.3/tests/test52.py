# Change of notation

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_52(self):
        k12, k21, ke, Ve, t = var ('k_12, k_21, k_e, V_e, t')
        x1,x2 = function ('x1,x2')
        params = [ke,Ve,k_12,k_21]
        edoA = Derivative(x1(t),t) - (-k12*x1(t) + k21*x2(t) - (Ve*x1(t))/(ke + x1(t)))
        edoB = Derivative(x2(t),t) - (k12*x1(t) - k21*x2(t))
        x1,x2 = indexedbase ('x1,x2')
        R = DifferentialRing (derivations = [t], blocks = [[x1,x2], params], parameters = params, notation = 'jet')
        edoA = R.normal_form (edoA)
        edoB = R.normal_form (edoB)
        self.assertEqual (edoA, (V_e*x1 + k_12*k_e*x1 + k_12*x1**2 - k_21*k_e*x2 - k_21*x1*x2 + k_e*x1[t] + x1[t]*x1)/(k_e + x1))
        self.assertEqual (edoB, -k_12*x1 + k_21*x2 + x2[t])

if __name__ == '__main__':
    unittest.main()
