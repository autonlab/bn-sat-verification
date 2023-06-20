import pytest
import os
import argparse
import logging
import sys

# change cwd to the directory of this file
print("Current working directory: ", os.getcwd())

pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(pardir, "src")
os.chdir(src_path)
sys.path.insert(0, src_path)

from typing import Dict, List, Tuple
from pysat.formula import CNF

from src.utils.cnf_json_parser import read_cnf_from_json
from src.verifications.pysat_solver import PySATSolver

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def get_data() -> Tuple[CNF, Dict, Dict]:
    '''
    Read the CNF and mappings from json file and return them
    
    Returns:
        A tuple of the CNF, a mapping from variable names to integers for the SAT solver, 
        and a mapping from integers to variable names for the SAT solver
    '''
    cnf, mapping_inverse, mapping, _ = read_cnf_from_json(
        os.path.join(os.getcwd(), 
                     "cnf_files/test_diagram.json")
        )
    return cnf, mapping, mapping_inverse

def convert_to_assumptions(to_set: Dict[str, int], mapping: Dict[str, int]) -> List[int]:
    '''
    Convert a dictionary of variables that are meant to be assumptions 
    to a list of assumptions (in the form of integers for the SAT solver)
    
    Args:
        to_set: A dictionary of variables that are meant to be assumptions
        mapping: A dictionary that maps variable names to integers for the SAT solver
    
    Returns:
        A list of assumptions (in the form of integers for the SAT solver)
    '''
    assumptions = []
    for var, value in to_set.items():
        if value == 1:
            assumptions.append(int(mapping[var]))
        else:
            assumptions.append(-int(mapping[var]))
    return assumptions
    
class TestEncodingWithSimpleQueries:
    def test_if_any_clauses(self, get_data):
        # Access the variable set up by the fixture
        cnf, _, _ = get_data
        assert len(cnf.clauses) > 0
    
    def test_if_satisfiable(self, get_data):
        cnf, _, _ = get_data
        assert PySATSolver().solve(cnf) != None
        
    def test_if_unsatisfiable_under_wrong_assumptions(self, get_data):
        '''
        test_binary_diagram should be unsatisfiable if we 
        set the GPA to 0 and WorkExperience to 0
        '''
        cnf, mapping, mapping_inverse = get_data
        
        to_set = {
            'Node_GPA_1': 1,
            'Node_WorkExperience_3': 1,
            'edge_1_3': 1,
            'edge_3_4': 0, # This edge renders the diagram UNSAT
            'x_1 = 1th value': 1,
            'x_2 = 0th value': 1,
            
            'Node_TRUE_4': 1, # True node should be true
            'Node_FALSE_5': 0, # False node should be false
        }
        
        assumpt = convert_to_assumptions(to_set, mapping)
        
        should_UNSSAT = PySATSolver().solve(cnf, assumptions=assumpt)
        assert not should_UNSSAT, "Should be UNSAT"
        
    def test_if_satisfiable_under_correct_assumptions(self, get_data):
        '''
        test_binary_diagram should be satisfiable if we
        set the GPA to 1 and WorkExperience to 1
        '''
        cnf, mapping, _ = get_data
        
        to_set = {
            'Node_GPA_1': 1,
            'Node_WorkExperience_2': 1,
            'edge_1_2': 1,
            'edge_2_4': 1,
            'x_1 = 0th value': 1,
            'x_2 = 0th value': 1,
            
            'Node_TRUE_4': 1, # True node should be true
            'Node_FALSE_5': 0, # False node should be false
        }
        
        assumpt = convert_to_assumptions(to_set, mapping)
        
        should_SAT = PySATSolver().solve(cnf, assumptions=assumpt)
        assert should_SAT, "Should be SAT"
        
    def test_if_consistent(self, get_data):      
        cnf, mapping, _ = get_data

        to_set = {
            'Node_GPA_1': 1, # First node should be true - we have to set it to true
            # This does not mean that we set the GPA to 1, but that we set the first node to true
            'Node_TRUE_4': 1, # True node should be true
            'Node_FALSE_5': 1, # False node should be false, but we set it to true
            # This should make the diagram inconsistent
        }

        assumpt = convert_to_assumptions(to_set, mapping)

        should_UNSAT = PySATSolver().solve(cnf, assumptions=assumpt)
        assert should_UNSAT == None, "Should be UNSAT, because the assumptions are inconsistent. \
            But it is SAT = wrong!!."
            
    def test_fail_if_two_nodes_at_the_same_level_are_active(self, get_data):
        cnf, mapping, _ = get_data
          
        to_set = {
            'Node_WorkExperience_2': 1,
            'Node_WorkExperience_3': 1,
        }

        assumpt = convert_to_assumptions(to_set, mapping)

        model = PySATSolver().solve(cnf, assumptions=assumpt)
        
        assert model == None, "Should be UNSAT"
            
        
    def test_fail_if_two_edges_at_the_same_level_are_active(self, get_data): 
        cnf, mapping, _ = get_data
        
        to_set = {
            'edge_2_4': 1,
            'edge_2_5': 1,
        }
                
        assumpt =  convert_to_assumptions(to_set, mapping)

        should_UNSAT = PySATSolver().solve(cnf, assumptions=assumpt)
        assert should_UNSAT == None, "Should be UNSAT, because the assumptions are inconsistent. \
            But it is SAT = wrong!!."            

    def test_if_at_most_one_path_is_active(self, get_data):
        cnf, mapping, _ = get_data
        
        
        # Go over all the outgoing edges of each of the nodes
        # and make sure that at most one of them is active 
        
        for i in range(len([x for x in mapping.keys() if x.startswith('Node')]) - 2):
            print(f"Testing if at most one path is active for node {i}")
            to_set = {            
                'Node_TRUE_4': 1, # True node should be true
                'Node_FALSE_5': 1, # False node should be false
            }
            
            for node in mapping.keys():
                if node.startswith(f'edge_{i}'):
                    to_set[node] = 1
                
            assumpt = convert_to_assumptions(to_set, mapping)

            should_UNSAT = PySATSolver().solve(cnf, assumptions=assumpt)
            assert should_UNSAT is None, f"Should be SAT, found a counterexample: {should_UNSAT}"