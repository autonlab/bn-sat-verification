import os
import json
from typing import Dict, Tuple
from pysat.formula import CNF

def __make_sure_path_is_in_src(path: str) -> str:
    dirname = os.path.dirname(__file__)
    pardirname = os.path.dirname(dirname)
    path = os.path.join(pardirname, path)
    return path
    

def save_cnf_to_json(cnf: CNF, mapping_inv: Dict, mapping: Dict, path: str) -> None:
    '''
    Save the cnf formula and the mapping to a json file
    '''
    path = __make_sure_path_is_in_src(path)
    
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
        
    mapping_inv = {str(key): str(value) for key, value in mapping_inv.items()}
    mapping = {str(key): str(value) for key, value in mapping.items()}
    
    with open(path, 'w') as f:
        json.dump({
            'cnf': cnf.clauses,
            'mapping_inv': mapping_inv,
            'mapping': mapping
        }, f, indent=4)
        
def read_cnf_from_json(path: str) -> Tuple[CNF, Dict, Dict]:
    '''
    Read the cnf formula and the mapping from a json file
    
    Returns:
        cnf: pysat CNF object
        mapping_inv: mapping from variable index to variable name
        mapping: mapping from variable name to variable index (in CNF)
    '''
    path = __make_sure_path_is_in_src(path)
    
    with open(path, 'r') as f:
        data = json.load(f)
        
    cnf = CNF()
    cnf.clauses = data['cnf']
    
    return cnf, data['mapping_inv'], data['mapping']