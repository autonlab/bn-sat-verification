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

# print("Current working directory: ", os.getcwd())

from typing import Dict, List, Tuple
from pysat.formula import CNF

from src.tseitin_encoding import add_node_clauses, read_cnf_from_json
from src.odd_parser import read_obdd_from_file
from src.pysat_solver import pysat_solver

logging.basicConfig(level=logging.DEBUG)



@pytest.fixture
def get_data() -> Tuple[CNF, Dict, Dict]:
    '''
    Read the CNF and mappings from json file and return them
    
    Returns:
        A tuple of the CNF, a mapping from variable names to integers for the SAT solver, 
        and a mapping from integers to variable names for the SAT solver
    '''
    cnf, mapping_inverse, mapping = read_cnf_from_json(
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
    
class TestBasicQueries:
    def test_if_any_clauses(self, get_data):
        # Access the variable set up by the fixture
        cnf, _, _ = get_data
        assert len(cnf.clauses) > 0
    
    def test_if_satisfiable(self, get_data):
        cnf, _, _ = get_data
        assert pysat_solver(cnf) != None
        
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
        
        should_UNSSAT = pysat_solver(cnf, set_variables=assumpt)
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
        
        should_SAT = pysat_solver(cnf, set_variables=assumpt)
        assert should_SAT, "Should be SAT"
