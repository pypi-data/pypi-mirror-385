# BaseFieldExtension with range indexed groups

from sympy import *
from DifferentialAlgebra import *
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_58(self):
        x,y = var('x,y')
        f,g,z = indexedbase('f,g,z')
        R = DifferentialRing(derivations = [x,y], blocks = [f,g,'(z)[oo:-1]'], parameters = ['(z)[0:oo](x)'], notation = 'jet')
        A = RegularDifferentialChain ([z[2]**2 - z[1], (z[1]-1)*(z[1]-x)], R, pretend=False)
        F = BaseFieldExtension (generators = ['(z)[0:oo]',g], relations = A)
        Z = F.generators ()
        self.assertEqual (Z, [g, '(z)[oo:-1]'])
        Z = F.relations().equations()
        self.assertEqual (Z, [-x*z[1] + x + z[1]**2 - z[1], -z[1] + z[2]**2])

if __name__ == '__main__':
    unittest.main()
