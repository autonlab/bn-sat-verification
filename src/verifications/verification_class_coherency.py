import logging
from typing import Dict, List, Tuple
from copy import deepcopy
from verifications.verification_case import VerificationCase
from verifications.solver_class import SATSolver
from verifications.verification_utils import strip_sinks
from pysat.formula import CNF
from utils.tseitin_transformation import tseitin_transformation_2

class VerificationCaseClassCoherency(VerificationCase):
        
        def __init__(self, name: str, 
                        map: Dict[str, int], 
                        sink_names_in_order: List[Tuple[str, str]],
                        only_check_sinks: List[int] | None = None 
                   ) -> None:
            '''
            `map`: Mapping from variable names to their values. 
                
            `map_name_vars`: Mapping from variable names to their values.  
                
            `sink_names_in_order`: Tuples of Sink name-pairs (true, false sinks) in ordinal order.
                  
            `only_check_sinks`: Check coherence only for sinks under given indices, where indices correspond 
            to `sink_names_in_order` positions. 
            '''
            super().__init__(name)
            self.map = map
            self.sink_names_in_order = sink_names_in_order
            self.only_check_sinks = only_check_sinks
            
            
        def verify(self, cnf: CNF, 
                   sat_solver: SATSolver, 
                   ) -> bool:
            '''
            Verify the class coherency of the model in multiclass classification setting.

            Parameters
                `cnf`: CNF formula of CNF class from PySAT. 
                 
                `sat_solver`: SAT solver - class that implements the method "solve".  
            '''
            if self.only_check_sinks is None:
                self.only_check_sinks = [i for i in range(len(self.sink_names_in_order))]
                
            n = len(self.sink_names_in_order)
            
            if n <= 2:
                # There is no point in checking anything as two classes are always adjacent 
                logging.info(f'Verification case #{self.name} is SAT. Because it has only two classes.')
                return True
            
            dnf_clauses = []
            for i in self.only_check_sinks:
                for j in self.only_check_sinks:
                    if i > j:
                        break
                    elif j - i <= 1:
                        # If we want to check only sinks that are not next to each other then skip the others
                        continue
                    else:
                        # Add Sink_i_true ^ Sink_j_true
                        dnf_clauses.append([
                            int(self.map[self.sink_names_in_order[i][0]]), 
                            int(self.map[self.sink_names_in_order[j][0]])
                            ])
                
            max_var = -1
            for clause in cnf.clauses:
                for lit in clause:
                    max_var = max(max_var, abs(lit))
                        
            verification_clauses = tseitin_transformation_2(dnf=dnf_clauses, max_var=max_var)
            
            altered_cnf = strip_sinks(cnf=cnf, sinks_map=self.sink_names_in_order, mapping=self.map).clauses
                                    
            verification_task_cnf = CNF(from_clauses=verification_clauses + altered_cnf)
            
            # Solve the verification task.
            self.sat_model = sat_solver.solve(cnf=verification_task_cnf)
            
            if self.sat_model is None:
                logging.debug(f'Verification case #{self.name} is UNSAT.')
                logging.debug(f'Verification case #{self.name} model: {self.sat_model}')
                self.set_result(True)
                return True
            else:
                logging.debug(f'Verification case #{self.name} is SAT.')
                logging.debug(f'Verification case #{self.name} model: {self.sat_model}')
                self.set_result(False)
                return False
            
        
            
