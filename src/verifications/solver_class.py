from abc import abstractmethod
from typing import List
from pysat.solvers import Solver
from pysat.formula import CNF

class SATSolver:
    
    @abstractmethod
    def solve(cnf: CNF, solver: Solver, assumptions: List[int] = []) -> List[int] | None:
        raise NotImplementedError("SATSolver.solve() is not implemented.")