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
            self.result_model = None
            
            for tpl in then_tuples:
                if tpl[1] not in ['>=', '<=']:
                    raise Exception('Only >= and <= are supported.')
            
            
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
            for var_name, sign, threshold in self.if_tuples:
                if sign not in ['<=', '>', '<', '>=', '==']:
                    raise Exception(f'Sign {sign} not supported.')
                IF.append((get_variable_values_list(variable_name=var_name), sign, int(threshold)))
                
            
            CNF_X = []
            for x, sign, threshold in IF:
                clause = []
                match sign:
                    case '>':
                        start = threshold + 1
                        end = len(x)
                    case '>=':
                        start = threshold
                        end = len(x)
                    case '<':
                        start = 0
                        end = threshold
                    case '<=':
                        start = 0
                        end = threshold + 1
                    case '==':
                        start = threshold
                        end = threshold + 1
                    case _:
                        raise Exception('Unexpected sign.')
                    
                for i in range(start, end):
                    clause.append(x[i])  
                CNF_X.append(clause)
        
            logging.debug(f'CNF_X: {CNF_X}') 
                   
            
            # THEN PART
            sinks_list = [] 
            
            if not self.binary:
               raise NotImplementedError('Not implemented for non-binary case.')
            else:
                _s = self.sink_names_in_order[0]
                if 'TRUE' in _s[0]: 
                    sinks_list.append(int(self.map[_s[1]])) # We want to have the false sink as the first one
                    sinks_list.append(int(self.map[_s[0]])) # and the true sink as the second one.
                else:
                    sinks_list.append(int(self.map[_s[0]]))
                    sinks_list.append(int(self.map[_s[1]]))
                                    
                logging.debug(f'Sinks: {sinks_list}')
                
            DNF_Y = []
            for _then_tuple in self.then_tuples:
                var_name, sign, threshold = _then_tuple 
                if var_name == 'Y':
                    if sign == '>=':
                        for i in range(0, threshold): # Only Y >= threshold. We add all Y's lower than threshold as contradiction.
                            DNF_Y.append([sinks_list[i]])
                    if sign == '<=':
                        if threshold + 1< len(sinks_list):
                            for i in range(threshold + 1, len(sinks_list)):
                                DNF_Y.append([sinks_list[i]])
                else:
                    raise Exception('Not implemented for non-binary case.')
            
            # CNF_Y, max_var = tseitin_transformation(DNF_Y, max_var + 1)
            if len(DNF_Y) == 0:
                # If there are no Y's, then we need to add that any Y sink would be a contradiction.
                # CNF_Y, max_var = tseitin_transformation([[sinks_list[0]], [sinks_list[1]]], max_var + 1)
                raise Exception('Not implemented for no Y case.')
            elif len(DNF_Y) == 1:
                # If there is only one Y, then we need to add that any other Y sink would be a contradiction.
                if DNF_Y[0][0] == sinks_list[0]:
                    CNF_Y = [[sinks_list[0]], [-sinks_list[1]]]
                elif DNF_Y[0][0] == sinks_list[1]:
                    CNF_Y = [[sinks_list[1]], [-sinks_list[0]]]
                else:
                    raise Exception('Unexpected DNF_Y[0][0] value.')
                    
            elif len(DNF_Y) == 2:
                # Use tseitin transformation to get the CNF of DNF_Y
                t = max_var + 1
                CNF_Y = []
                CNF_Y.append([-DNF_Y[0][0], t])
                CNF_Y.append([-DNF_Y[1][0], t])
                CNF_Y.append([DNF_Y[0][0], DNF_Y[1][0], -t])
                max_var = t
            else:
                # TODO: Implement for DNF_Y longer than 2 clauses.
                raise Exception('Not implemented for DNF_Y longer than 2 clauses.')
            
            logging.debug(f'DNF_Y: {DNF_Y}')
            # Translate and print DNF_Y
            for clause in DNF_Y:
                _c = []
                for lit in clause:
                    _c.append(self.map_inverse[lit])
                logging.debug(f'Clause: {_c}')
            logging.debug(f'CNF_Y: {CNF_Y}, \
                real_names: {[[self.map_inverse[abs(lit)] for lit in clause] for clause in CNF_Y]}')
            
            final_cnf = deepcopy(altered_cnf) + CNF_X + CNF_Y
            
            
            outcome = sat_solver.solve(cnf=CNF(from_clauses=final_cnf))
            
            self.result_model = outcome
            
            
            if outcome is None:
                logging.debug(f'Verification case #{self.name} is UNSAT.')
                logging.debug(f'Verification case #{self.name} model: {None}')
                self.set_result(True)
                return True
            else:
                logging.debug(f'Verification case #{self.name} is SAT.')
                logging.debug(f'Verification case #{self.name} model: {outcome}')
                
                # Print actual names of true literals in the model
                for lit in outcome:
                    if lit > 0 and lit in self.map_inverse.keys():
                        logging.debug(f'Literal [{lit}]: {self.map_inverse[lit]}')
                self.set_result(False)
                return False
            
            
            raise Exception('Unexpected outcome of the verification task.')
                
