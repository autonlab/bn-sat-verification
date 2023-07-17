import logging
from typing import Dict, List, Tuple
from copy import deepcopy
from verifications.verification_case import VerificationCase
from verifications.solver_class import SATSolver
from verifications.verification_utils import strip_sinks, A_greater_than_B
from pysat.formula import CNF
from utils.tseitin_transformation import tseitin_transformation_2, tseitin_transformation

class VerificationIfThenRules(VerificationCase):
        
        def __init__(self, name: str, 
                        map: Dict[str, int], 
                        sink_names_in_order: List[Tuple[str, str]],
                        if_tuples: Tuple[str, int],
                        then_tuples: Tuple[str, int],
                        map_name_vars: Dict[str, List[str]],
                        binary: bool = False
                   ) -> None:
            '''
            `map`: Mapping from variable names to their values. 
                
            `map_name_vars`: Mapping from variable names to their values.  
                
            `sink_names_in_order`: Tuples of Sink name-pairs (true, false sinks) in ordinal order.
                  

            '''
            super().__init__(name)
            self.map = map
            self.map_inverse = {int(v): k for k, v in self.map.items()}
            self.sink_names_in_order = sink_names_in_order
            self.sinks_count = len(self.sink_names_in_order)
            self.map_name_vars = map_name_vars
            self.binary = binary
            self.if_tuples = if_tuples
            self.then_tuples = then_tuples
            
            
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
               
            altered_cnf = strip_sinks(cnf=cnf, sinks_map=self.sink_names_in_order, mapping=self.map)  
        
            def get_variable_values_list(variable_name: str):
                names = sorted(
                    [name for name in self.map_name_vars[variable_name]], 
                    key=lambda x: int(x.split('=')[1].split('th')[0])
                    )
                variable_values = [int(self.map[name]) for name in names]
                return variable_values
            
            # IF PART
            IF = []
            for _if_tuple in self.if_tuples:
                var_name, threshold = _if_tuple
                IF.append((get_variable_values_list(variable_name=var_name), threshold))
                
            def all_combinations(_DNF, _IF, _i, _path):
                '''Assuming all >= for thresholds'''
                x, threshold = _IF[_i]
                for j in range(threshold, len(x)):
                    next_path = _path + [x[j]]
                    if _i == len(_IF) - 1:
                        _DNF.append(next_path)
                    else:
                        all_combinations(_DNF, _IF, _i + 1, next_path)

                return _DNF
            
            DNF_X = all_combinations(_DNF=[], _IF=IF, _i=0, _path=[])
            
            # # Check if any DNF_X clause is longer than 2 literals. If so, raise an error.
            # for clause in DNF_X:
            #     if len(clause) > 2:
            #         raise Exception('Not implemented for DNF_X clauses longer than 2 literals.')
            #     if len(clause) < 2:
            #         raise Exception('Not implemented for DNF_X clauses shorter than 2 literals.')
                
            # Use tseitin transformation to get the CNF of DNF_X
            CNF_X, max_var = tseitin_transformation(DNF_X, max_var + 1)
            
            logging.debug(f'DNF_X: {DNF_X}')      
            # Translate and print DNF_X
            for clause in DNF_X:
                _c = []
                for lit in clause:
                    _c.append(self.map_inverse[lit])
                logging.debug(f'Clause: {_c}')  
                   
            
            # THEN PART
            sinks_list = []
            
            if not self.binary:
               raise NotImplementedError('Not implemented for non-binary case.')
            else:
                _s = self.sink_names_in_order[0]
                if 'TRUE' in _s[0]: 
                    sinks_list.append(int(self.map[_s[0]]))
                    sinks_list.append(int(self.map[_s[1]]))
                else:
                    sinks_list.append(int(self.map[_s[1]]))
                    sinks_list.append(int(self.map[_s[0]]))
                                    
                logging.debug(f'Sinks: {sinks_list}')
                
            DNF_Y = []
            for _then_tuple in self.then_tuples:
                var_name, threshold = _then_tuple 
                if var_name == 'Y':
                    for i in range(0, threshold): # Only Y >= threshold. We add all Y's lower than threshold as contradiction.
                        DNF_Y.append([sinks_list[i]])
                else:
                    raise Exception('Not implemented for non-binary case.')
            
            CNF_Y, max_var = tseitin_transformation(DNF_Y, max_var + 1)
            # if len(DNF_Y) == 0:
            #     raise Exception('DNF_Y is empty.')
            # elif len(DNF_Y) == 1:
            #     CNF_Y = [[DNF_Y[0][0]]]
            # elif len(DNF_Y) == 2:
            #     # Use tseitin transformation to get the CNF of DNF_Y
            #     t = max_var + 1
            #     CNF_Y = []
            #     CNF_Y.append([-DNF_Y[0][0], t])
            #     CNF_Y.append([-DNF_Y[1][0], t])
            #     CNF_Y.append([DNF_Y[0][0], DNF_Y[1][0], -t])
            #     max_var = t
            # else:
            #     raise Exception('Not implemented for DNF_Y longer than 2 clauses.')
            
            logging.debug(f'DNF_Y: {DNF_Y}')
            # Translate and print DNF_Y
            for clause in DNF_Y:
                _c = []
                for lit in clause:
                    _c.append(self.map_inverse[lit])
                logging.debug(f'Clause: {_c}')
            
            final_cnf = deepcopy(altered_cnf) + CNF_X + CNF_Y
            
            
            outcome = sat_solver.solve(cnf=CNF(from_clauses=final_cnf))
            
            if outcome is None:
                logging.debug(f'Verification case #{self.name} is UNSAT.')
                logging.debug(f'Verification case #{self.name} model: {None}')
                self.set_result(True)
                return True
            else:
                logging.debug(f'Verification case #{self.name} is SAT.')
                logging.debug(f'Verification case #{self.name} model: {outcome}')
                self.set_result(False)
                return False
            
            
            raise Exception('Unexpected outcome of the verification task.')
                
