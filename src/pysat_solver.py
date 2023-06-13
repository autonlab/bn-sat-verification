import logging

from typing import List
from pysat.solvers import Solver, Glucose3
from pysat.formula import CNF


def pysat_solver(cnf: CNF, set_variables: List[int] = [], solver: Solver = Glucose3()) -> List[int] | None:
    '''
    Solve the given cnf formula with the given solver using pysat library.
    
    Args:
        cnf: The cnf formula to be solved.
        set_variables: The variables to be set to true.
        solver: The solver to be used.
    
    Returns:
        The model if the formula is satisfiable, None otherwise.
    '''
    
    # Set variables to be frozen
    if set_variables:
        for variable in set_variables:
            cnf.append(clause=[variable])

    # Add cnf formula to solver
    solver.append_formula(cnf)

    if solver.solve():
        logging.debug(f'SAT')
        sat_model = solver.get_model()
        logging.debug(f'SAT MODEL: {sat_model}')
    else:
        logging.debug(f'UNSAT')
        sat_model = None
    
    return sat_model

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
    
    pysat_solver(cnf, set_variables=[1, 3])