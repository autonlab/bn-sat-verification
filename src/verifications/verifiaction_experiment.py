from copy import deepcopy
from typing import Dict, List, Tuple
from pysat.formula import CNF
import timeit
import logging

from verifications.solver_class import SATSolver
from verifications.verification_case import VerificationCase

class VerificationExperiment:
    
    def __init__(self, cnf: CNF, sat_solver: SATSolver) -> None:
        self.cnf = cnf
        self.sat_solver = sat_solver
        self.verification_cases: List[VerificationCase] = []
        self.results: Dict[VerificationCase, Dict] = {}
        
    def add_verification_case(self, verification_case: VerificationCase) -> None:
        '''
        Add a verification case to the experiment.
        '''
        self.verification_cases.append(verification_case)
        
    def add_multiple_verification_cases(self, verification_cases: List[VerificationCase]) -> None:
        '''
        Add multiple verification cases to the experiment.
        '''
        self.verification_cases.extend(verification_cases)
        
    def run_verification_case(self, verification_case: VerificationCase) -> Tuple[bool, float]:
        '''
        Run a single verification case.
        '''
        start_time = timeit.default_timer()
        is_SAT: bool = verification_case.verify(deepcopy(self.cnf), self.sat_solver)
        end_time = timeit.default_timer()
        verification_case.set_result(is_SAT)
        
        logging.info(f'-'*80)
        logging.info(f"Verification case: '{verification_case.name}' is {'PASSED' if is_SAT else 'FAILED'} ({'UNSAT' if is_SAT else 'SAT'}).")
        logging.info(f"Verification case: '{verification_case.name}' took {1000 * (end_time - start_time):.1f} ms.")
        logging.info(f'-'*80)
        
        return is_SAT, end_time - start_time
    
    def run_all_verification_cases(self) -> None:
        '''
        Run all verification cases.
        '''
        for verification_case in self.verification_cases:
            is_SAT, exec_time = self.run_verification_case(verification_case)
            self.results[verification_case] = {"is_SAT": is_SAT, "exec_time": exec_time}
            
    def get_results(self) -> Dict[VerificationCase, Dict]:
        '''
        Return the results of the experiment.
        '''
        return self.results
    
    def clear_all_results(self) -> None:
        '''
        Clear all results.
        '''
        self.results = {}
        
    def clear_all_verification_cases(self) -> None:
        '''
        Clear all verification cases.
        '''
        self.verification_cases = []
            