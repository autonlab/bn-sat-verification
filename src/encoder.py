from abc import abstractmethod
from collections import defaultdict
from pysat.formula import CNF
from typing import Dict, List, Tuple
from utils.cnf_json_parser import save_cnf_to_json, read_cnf_from_json
from utils.node import Node

class Encoder:
    
    def __init__(self) -> None:
        self.mapping: Dict[str, int] = {}
        self.mapping_inv: Dict[int, str] = {}
        self.mapping_variable_xval: Dict[str, List[str]] = defaultdict(set) # Map from variable name to x_i = j
        self.cnf: CNF = CNF()
        
    @staticmethod
    def _exactly_one(literals: List[int]) -> List[List[int]]:
        '''
        Encodes that exactly one of the literals is true
        '''
        
        def at_least_one(literals: List[int]) -> List[int]:
            '''
            Encodes that at least one of the literals is true.
            So it is OR of all variables.
            '''
            return literals
        
        def at_most_one(literals: List[int]) -> List[List[int]]:
            '''
            Encodes that at most one of the literals is true
            This 
            '''
            clauses = []
            for i in range(len(literals)-1):
                for j in range(i+1, len(literals)):
                    clauses.append([-literals[i], -literals[j]])
                    
            return clauses

        return [at_least_one(literals)] + at_most_one(literals)
    
    @staticmethod
    def at_most_one(literals: List[int]) -> List[List[int]]:
        '''
        Encodes that at most one of the literals is true
        This 
        '''
        clauses = []
        for i in range(len(literals)-1):
            for j in range(i+1, len(literals)):
                clauses.append([-literals[i], -literals[j]])
            
        return clauses


    @abstractmethod
    def encode_to_cnf(self, odd: Dict[int, Node]) -> Tuple[CNF, Dict, Dict]:
        '''
        Encode the ODD to a CNF formula.
        '''
        pass

    def save_to_json(self, path) -> None:
        '''
        Save the CNF formula to a JSON file.
        Includes the mapping from variable names to variable indices.
        '''
        save_cnf_to_json(path,
                        cnf=self.cnf,
                        map_inv=self.mapping_inv,
                        map=self.mapping,
                        map_names_vars=self.mapping_variable_xval)
    
    def load_from_json(self, path) -> None:
        '''
        Load the CNF formula with mappings from a JSON file.
        Populate Encoder variables with the loaded values.
        '''
        self.cnf, self.mapping_inv, self.mapping, self.mapping_variable_xval = read_cnf_from_json(path)