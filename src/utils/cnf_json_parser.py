import os
import json
import logging
from typing import Dict, Tuple
from pysat.formula import CNF

def __make_sure_path_is_in_src(path: str) -> str:
    dirname = os.path.dirname(__file__)
    pardirname = os.path.dirname(dirname)
    path = os.path.join(pardirname, path)
    return path
    

def save_cnf_to_json(path: str, **kwargs) -> None:
    '''
    Save the cnf formula and the mapping to a json file
    '''
    path = __make_sure_path_is_in_src(path)
    
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
        
    mapping_inv = {str(key): str(value) for key, value in kwargs['map_inv'].items()}
    mapping = {str(key): str(value) for key, value in kwargs['map'].items()}
    
    to_save = {k:v for k,v in kwargs.items()}
    to_save['cnf'] = kwargs['cnf'].clauses
    to_save['map_inv'] = mapping_inv
    to_save['map'] = mapping
    to_save['map_names_vars'] = {str(key): list(value) for key, value in kwargs['map_names_vars'].items()}
    
    with open(path, 'w') as f:
        json.dump(to_save, f, indent=2)
        
def read_cnf_from_json(path: str) -> Tuple[CNF, Dict, Dict, Dict]:
    '''
    Read the cnf formula and the mapping from a json file
    
    Returns:
        cnf: pysat CNF object
        map_inv: mapping from variable index to variable name
        map: mapping from variable name to variable index (in CNF)
        map_names_vars: mapping from variable name to variable index (in the original formula)
    '''
    path = __make_sure_path_is_in_src(path)
    
    with open(path, 'r') as f:
        data = json.load(f)
        
    cnf = CNF()
    cnf.clauses = data['cnf']
    
    return cnf, data['map_inv'], data['map'], data['map_names_vars']

def read_unstructured_from_json(path: str) -> Dict:
    '''
    Read json without parsing anything
    '''
    path = __make_sure_path_is_in_src(path)
    
    with open(path, 'r') as f:
        data = json.load(f)
        
    return data

    
def print_with_names(cnf: CNF, mapping_inv: Dict) -> None:
    '''
    Print the cnf formula with the names of the variables
    '''
    for clause in cnf.clauses:
        logging.debug([mapping_inv[abs(lit)] if lit > 0 else f'-{mapping_inv[abs(lit)]}' for lit in clause])

def print_mapping(mapping: Dict) -> None:
    '''
    Print the mapping in a nice way
    '''
    for key, value in mapping.items():
        logging.debug(f'{key:{" "}{"<"}{3}}: {value}')
