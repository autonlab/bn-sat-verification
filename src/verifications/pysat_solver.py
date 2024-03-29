import logging
from typing import List
from pysat.solvers import Solver, Maplesat, Cadical153, Glucose3, Minisat22
from pysat.formula import CNF

from verifications.solver_class import SATSolver

class PySATSolver(SATSolver):
    
    def solve(self, cnf: CNF, solver: Solver = None, assumptions: List[int] = []) -> List[int] | None:
        '''
        Solve the given cnf formula with the given solver using pysat library.
        
        Args:
            cnf: The cnf formula to be solved.
            solver: The solver to be used. By default, Glucose3 is used.
            assumptions: The variables to be set to true. By default, no assumptions are made.
        
        Returns:
            The model if the formula is satisfiable, None otherwise.
        '''
        if solver is None:
            self.solver = Minisat22()
        else:
            self.solver = solver
            
        self.cnf = cnf
        self.assumptions = assumptions
        
        # Add cnf formula to solver
        self.solver.append_formula(cnf)

        if self.solver.solve(assumptions=self.assumptions):
            logging.debug(f'SAT')
            sat_model = self.solver.get_model()
            logging.debug(f'SAT MODEL: {sat_model}')
        else:
            logging.debug(f'UNSAT')
            sat_model = None
        
        return sat_model
    
    def enumerate_all_SAT_models(self) -> List[List[int]]:
        '''
        Enumerate all SAT models for the given cnf formula.
        
        Returns:
            A list of all SAT models.
        '''
        return [m for m in self.solver.enum_models()]

if __name__ == "__main__":
    # -------------------------------
    # This is the example that encodes following OBDD
    #                        0 --> False
    #   0 --> WorkExperience 1 --> True 
    # GPA
    #   1 --> WorkExperience 1 --> True
    #                        0 --> False
    # -------------------------------
    cnf = CNF()
    cnf.append([1, -2])
    cnf.append([3, -2])
    cnf.append([-1, -3, 2])
    cnf.append([1, 4])
    cnf.append([-1, -4])
    cnf.append([4, -5])
    cnf.append([3, -5])
    cnf.append([-4, -3, 5])
    cnf.append([-2, 6])
    cnf.append([-5, 6])
    cnf.append([2, 5, -6])

    # Top-level OR 
    cnf.append([6])
    
    logging.basicConfig(level=logging.DEBUG)
    
    PySATSolver().solve(cnf, assumptions=[1, 3])