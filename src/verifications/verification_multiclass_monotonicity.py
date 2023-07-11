import logging
from typing import Dict, List, Tuple
from copy import deepcopy
from verifications.verification_case import VerificationCase
from verifications.solver_class import SATSolver
from verifications.verification_utils import strip_sinks, A_greater_than_B
from pysat.formula import CNF
from utils.tseitin_transformation import tseitin_transformation_2

class VerificationCaseMulticlassMonotonicity(VerificationCase):
        
        def __init__(self, name: str, 
                        map: Dict[str, int], 
                        sink_names_in_order: List[Tuple[str, str]],
                        variable_to_verify: str,
                        map_name_vars: Dict[str, List[str]]
                   ) -> None:
            '''
            `map`: Mapping from variable names to their values. 
                
            `map_name_vars`: Mapping from variable names to their values.  
                
            `sink_names_in_order`: Tuples of Sink name-pairs (true, false sinks) in ordinal order.
                  

            '''
            super().__init__(name)
            self.map = map
            self.sink_names_in_order = sink_names_in_order
            self.sinks_count = len(self.sink_names_in_order)
            self.variable_to_verify = variable_to_verify
            self.variable_to_verify_index = self.map[variable_to_verify]
            self.map_name_vars = map_name_vars
            
            
        def verify(self, cnf: CNF, 
                   sat_solver: SATSolver, 
                   ) -> bool:
            '''
            Verify the monotonicity of the model in multiclass classification setting.

            Parameters
                `cnf`: CNF formula of CNF class from PySAT. 
                 
                `sat_solver`: SAT solver - class that implements the method "solve".  
            '''      
            max_var = -1
            for clause in cnf.clauses:
                for lit in clause:
                    max_var = max(max_var, abs(lit))
                        
            altered_cnf = strip_sinks(cnf=cnf, sinks_map=self.sink_names_in_order, mapping=self.map).clauses  
            
            models = [deepcopy(altered_cnf.clauses) for _ in range(3)]
            offsets = [0, max_var, 2 * max_var]
            
            # Translate models by offsets
            for i in range(3):
                for clause in models[i]:
                    for j in range(len(clause)):
                        clause[j] += offsets[i]
            
            variable_values = [self.map[name] for name in self.map_name_vars[self.variable_to_verify]]
            
            
            # --- VAR_ORD --- #
            # X2 > X1
            VAR_ORD, max_var = A_greater_than_B(a=[a + offsets[1] for a in variable_values], 
                             b=variable_values, 
                             max_var=3 * max_var) 
            # X3 > X2
            VAR_ORD, max_var += A_greater_than_B(a=[a + offsets[2] for a in variable_values],
                                b=[a + offsets[1] for a in variable_values], 
                                max_var=3 * max_var)
            # X3 > X1
            VAR_ORD, max_var += A_greater_than_B(a=[a + offsets[2] for a in variable_values],
                                b=variable_values, 
                                max_var=3 * max_var)
            
            
            LHL = []
            HLH = []
            
            true_sinks = []
            for sinks in self.sink_names_in_order:
                if 'TRUE' in sinks[0]:
                    true_sinks.append(self.map[sinks[0]])
                else:
                    true_sinks.append(self.map[sinks[1]])
            
            # --- LHL --- # 
            # Y2 > Y1
            LHL, max_var += A_greater_than_B(a=[a + offsets[1] for a in true_sinks], 
                             b=true_sinks, 
                             max_var=3 * max_var)
            # Y2 > Y3
            LHL, max_var += A_greater_than_B(a=[a + offsets[1] for a in true_sinks],
                                b=[a + offsets[2] for a in true_sinks], 
                                max_var=3 * max_var)
            
            # --- HLH --- #
            # Y2 < Y1
            HLH, max_var += A_greater_than_B(a=true_sinks,
                                b=[a + offsets[1] for a in true_sinks], 
                                max_var=3 * max_var)
            # Y2 < Y3
            HLH, max_var += A_greater_than_B(a=[a + offsets[2] for a in true_sinks],
                                b=[a + offsets[1] for a in true_sinks], 
                                max_var=3 * max_var)
            

            # Create two separate verification tasks for LHL and HLH.
            verif1 = models[0] + models[1] + models[2] + VAR_ORD + LHL
            verif1 = deepcopy(verif1)
            
            verif2 = models[0] + models[1] + models[2] + VAR_ORD + HLH
            verif2 = deepcopy(verif2)
            
            
            outcome1 = sat_solver.solve(cnf=CNF(from_clauses=verif1))
            outcome2 = sat_solver.solve(cnf=CNF(from_clauses=verif2))
            
            if outcome1 is None and outcome2 is None:
                logging.debug(f'Verification case #{self.name} is UNSAT.')
                logging.debug(f'Verification case #{self.name} model: {self.sat_model}')
                self.set_result(True)
                return True
            
            if outcome1 is not None or outcome2 is not None:
                logging.debug(f'Verification case #{self.name} is SAT.')
                if outcome1 is not None:
                    self.sat_model = outcome1
                    logging.debug(f'Verification case #{self.name} LHL model: {self.sat_model}')
                elif outcome2 is not None:
                    self.sat_model = outcome2
                    logging.debug(f'Verification case #{self.name} HLH model: {self.sat_model}')
                self.set_result(False)
                return False
                
