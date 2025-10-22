# Michaelis-Menten reduction

from sympy import *
from DifferentialAlgebra import DifferentialRing, RegularDifferentialChain, BaseFieldExtension, function
import unittest

class TestDifferentialAlgebra(unittest.TestCase):
    def test_03(self):
        leader,order,rank = var ('leader,order,rank')
        derivative = function ('derivative')
        
        t = var('t')
        km1,k1,k2 = var('km1,k1,k2')
        F1,E,S,ES,P = function('F1,E,S,ES,P')
        params = [km1,k1,k2]
        
        syst = [Derivative(E(t),t) + F1(t) - k2*ES(t), Derivative(S(t),t) + F1(t), Derivative(ES(t),t) + k2*ES(t) - F1(t), Derivative(P(t),t) - k2*ES(t), k1*E(t)*S(t) - km1*ES(t) ]
        
        Field = BaseFieldExtension (generators = params)
        R = DifferentialRing (derivations = [t], blocks = [F1, [E,ES,P,S], params], parameters = params)
        ideal = R.RosenfeldGroebner (syst, basefield = Field)
        eqns = [ C.equations (solved = True) for C in ideal ]
        ideal [0].equations (solved = True, selection = Eq(leader,derivative (S(t))))
        
        E0,ES0,P0,S0,K,V_max = var ('E0,ES0,P0,S0,K,V_max')
        params = [km1,k1,k2,E0,ES0,P0,S0,K,V_max]
        R = DifferentialRing (blocks = [F1, [ES,E,P,S], params], parameters = params, derivations = [t])
        
        relations_among_params = RegularDifferentialChain ([P0, ES0, Eq(K,km1/k1), Eq(V_max,k2*E0)], R)
        
        Field = BaseFieldExtension (generators = params, relations = relations_among_params)
        newsyst = syst + [Eq(E(t) + ES(t), E0 + ES0), Eq(S(t) + ES(t) + P(t), S0 + ES0 + P0)]
        ideal = R.RosenfeldGroebner (newsyst, basefield = Field)
        
        self.assertEqual (ideal[0].normal_form (Derivative(P(t),t)), V_max * S(t) / (K + S(t)))

if __name__ == '__main__':
    unittest.main()
