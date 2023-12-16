from abc import abstractmethod
from typing import List

from verifications.solver_class import SATSolver

class VerificationCase:
    
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.is_SAT: bool
        self.result_model: dict | None = None
        self.solver: SATSolver | None = None
    
    @abstractmethod    
    def verify(self, **kwargs) -> bool:
        raise NotImplementedError("VerificationCase.verify() is not implemented.") 
    
    def set_result(self, is_SAT: bool) -> None:
        self.is_SAT = is_SAT
        
    def set_sat_solver(self, sat_solver: SATSolver) -> None:
        self.solver = sat_solver
        
    def set_name(self, name: str) -> None:
        self.name = name
        
    def get_result_model(self) -> dict | None:
        return self.result_model
    
    def get_all_models(self) -> List[dict]:
        return self.solver.enumerate_all_SAT_models()
        
    def __hash__(self) -> int:
        return hash(self.name + str(self.__class__))
    
    def __str__(self) -> str:
        return f'Verification case #{self.name}'