import logging
from typing import Dict, List
from copy import deepcopy
from verifications.verification_case import VerificationCase
from verifications.solver_class import SATSolver
from pysat.formula import CNF
from utils.tseitin_transformation import tseitin_transformation_2

class VerificationCaseBinaryMonotonicity(VerificationCase):
        
        def __init__(self, name: str) -> None:
            super().__init__(name)
            
        def verify(self, cnf: CNF, 
                   map: Dict[str, int], 
                   sat_solver: SATSolver, 
                   variable_to_verify: str, 
                   map_name_vars: Dict[str, List[str]]) -> bool:
            '''
            Verify the monotonicity of the model in binary classification setting.

            Parameters
                `cnf`: CNF formula of CNF class from PySAT.
                `map`: Mapping from variable names to their values.
                `sat_solver`: SAT solver - class that implements the method "solve".
                `variable_to_verify`: Variable name to verify. e.g. "WorkExperience".
                `map_name_vars`: Mapping from variable names to their values.
            '''
            
            # We need to create two copies of the CNF formula.
            formula_1 = deepcopy(cnf.clauses)
            formula_2 = deepcopy(cnf.clauses)
            
            # Find max variable in formula_1.
            max_var = 0
            for clause in formula_1:
                for literal in clause:
                    max_var = max(max_var, abs(literal))
            
            # Translate entire formula_2 by max_var.
            for i, clause in enumerate(formula_2):
                for j, literal in enumerate(clause):
                    formula_2[i][j] = (abs(literal) + max_var) * (-1 if literal < 0 else 1)

            # We need to track "variable_to_verify" in both copies.
            x_cat_values = map_name_vars[variable_to_verify]
            x_cat_values = [int(map[x]) for x in x_cat_values]
            x_cat_values = sorted(x_cat_values)
            
            # Keep track of variable of interest in both copies.
            x_cat_values_1 = x_cat_values
            x_cat_values_2 = [x + max_var for x in x_cat_values]
            
            # Keep track of the TRUE and FALSE nodes in both copies.
            true_node_1 = [int(map[val]) for val in map.keys() if val.startswith('Node_TRUE')][0]
            true_node_2 = true_node_1 + max_var
            
            false_node_1 = [int(map[val]) for val in map.keys() if val.startswith('Node_FALSE')][0]
            false_node_2 = false_node_1 + max_var
            
            # Modify the formula_1 to alter the TRUE and FALSE nodes.
            # Set the first model to evaluate to false
            # # and leave the second model to evaluate to true.
            for i, clause in enumerate(formula_1):
                if clause == [true_node_1]:
                    formula_1[i] = [-true_node_1] # Modify T to ~T
                if clause == [-false_node_1]:
                    formula_1[i] = [false_node_1] # Modify ~F to F
                    
            # Now we need to enforce the increasing order of 
            # the variable values of interest.
            # Variable index in the formula_1, should always be greater 
            # than variable index in the formula_2.
            verif_clauses_DNF = []
            
            for i in range(1, len(x_cat_values_1)):
                for j in range(i):
                    verif_clauses_DNF.append([x_cat_values_1[i], x_cat_values_2[j]])
                
            # # Convert DNF to CNF using Tseitin transformation.
            verification_clauses = tseitin_transformation_2(verif_clauses_DNF, max_var * 2)
                
            verification_task_cnf = CNF(from_clauses=verification_clauses + formula_1 + formula_2)
            
            # Solve the verification task.
            sat_model = sat_solver.solve(cnf=verification_task_cnf)
            
            # UNSAT means that the model is monotonic.
            if sat_model is None:
                logging.info(f'Verification case #{self.name} is UNSAT.')
                logging.info(f'Verification case #{self.name} model: {sat_model}')
                self.set_result(True)
                return True
            # SAT means that the model is not monotonic.
            else:
                logging.info(f'Verification case #{self.name} is SAT.')
                logging.info(f'Verification case #{self.name} model: {sat_model}')
                self.set_result(False)
                return False
            
        
            
