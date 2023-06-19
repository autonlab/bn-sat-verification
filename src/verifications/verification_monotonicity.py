from verifications.verification_case import VerificationCase
from verifications.solver_class import SATSolver
from pysat.formula import CNF

class VerificationCaseMonotonicity(VerificationCase):
        
        def __init__(self, name: str) -> None:
            super().__init__(name)
            
        def verify(self, cnf: CNF, sat_solver: SATSolver) -> bool:
            '''
            Verify the monotonicity of the model.
            '''
            raise NotImplementedError("VerificationCaseMonotonicity.verify() is not implemented.")