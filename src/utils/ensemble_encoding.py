from typing import List, Dict, Tuple
from utils.cnf_json_parser import read_cnf_from_json, save_cnf_to_json
from pysat.formula import CNF

def merge_two_models(cnf1: List[List[int]], 
                     cnf2: List[List[int]],
                     map1: Dict[str, int],
                     map2: Dict[str, int],
                     inverse_map1: Dict[int, str],
                     inverse_map2: Dict[int, str],
                     map_names_vars1: Dict[str, List[str]],
                     map_names_vars2: Dict[str, List[str]],
                     model_index: int
                     ) -> Tuple[List[List[int]], Dict[int, str], Dict[str, int], Dict[str, str]]:
    '''
    Merge two models into a single model by combining the variables.
    All variables in both models that are the same will be combined in order to create a single, consistent model.
    '''
    
    
    common_indexer = 1
    common_map = {}
    common_map_names_vars = {}
    common_map_vars_names = {} 
    
    for _mapnames in [map_names_vars1, map_names_vars2]:
        for vname, vvalueslist in _mapnames.items():
            
            if vname not in common_map_names_vars:
                common_map_names_vars[vname] = set()
            
            for k in vvalueslist:
                ith_value = k.split('=')[1]
                name = f'{vname}={ith_value}'
                if name not in common_map:
                    common_map[name] = common_indexer
                    common_indexer += 1
                    
                common_map_names_vars[vname].add(name)
                common_map_vars_names[k] = vname
               
    first = (cnf1, map1, inverse_map1)
    second = (cnf2, map2, inverse_map2)
     
    for m_index, _map in enumerate([map1, map2]):
        for name in _map:
            if name.startswith('x_') or '=' in name:
                continue
            else:
                if m_index == 1:
                    common_map[f'{name}__{model_index}'] = common_indexer
                else:
                    common_map[f'{name}'] = common_indexer
                common_indexer += 1
    
    new_cnf = []
    for m_index, (_cnf, _map, _inverse) in enumerate([first, second]):
        for clause in _cnf:
            new_clause = [] 
            for literal in clause:
                sign = -1 if literal < 0 else 1
                literal_int_as_string = abs(literal)
                literal_name = _inverse[literal_int_as_string]
                
                if literal_name.startswith('x_') or '=' in literal_name:
                    ith_value = literal_name.split('=')[1]
                    name = f'{common_map_vars_names[literal_name]}={ith_value}'
                else:
                    if m_index == 1:
                        name = f'{literal_name}__{model_index}'
                    else:
                        name = literal_name
                    
                new_literal = common_map[name] * sign
                new_clause.append(new_literal)
        
            new_cnf += [new_clause]
                
    common_map_inverse = __create_inverse_map(common_map) 
    
    return new_cnf, common_map_inverse, common_map, common_map_names_vars
 
def __create_inverse_map(maping: Dict[str, int]) -> Dict[int, str]:
    '''
    Creates an inverse map from the given map
    '''
    inverse_map = {}
    for key, value in maping.items():
        inverse_map[value] = key

    return inverse_map
    

def ensemble_encode(cnf_files: List[str]) -> Tuple[CNF, Dict[int, str], Dict[str, int], Dict[str, str]]:
    '''
    Encodes a list of CNF files to a single CNF file
    
    Args:
        - cnf_files: A list of CNF files
    
    Returns:
        - The CNF file
        - The inverse maping of the variables
        - The maping of the variables
        - The maping of the variable names
    '''
    ensemble_cnf = []
    ensemble_map = {}
    ensemble_inverse_map = {}
    ensemble_map_var_names = {}
    
    for idx, cnf_file in enumerate(cnf_files):
        cnf, inverse_map, maping, map_var_names = read_cnf_from_json(cnf_file)
        
        inverse_map = {int(k):v for k,v in inverse_map.items()}
        maping = {k:int(v) for k,v in maping.items()}
        
        
        if not ensemble_cnf: 
            ensemble_cnf = cnf.clauses
            ensemble_map = maping
            ensemble_inverse_map = inverse_map
            ensemble_map_var_names = map_var_names
        else:
            ensemble_cnf, ensemble_inverse_map, ensemble_map, ensemble_map_var_names = merge_two_models(
                                ensemble_cnf, 
                                cnf.clauses, 
                                ensemble_map, 
                                maping, 
                                ensemble_inverse_map,
                                inverse_map,
                                ensemble_map_var_names, 
                                map_var_names,
                                idx
                                )
        
        
    ensemble_inverse_map = __create_inverse_map(ensemble_map)
    
    _cnf = CNF()
    for clause in ensemble_cnf:
        _cnf.append(clause)
    
    return _cnf, ensemble_inverse_map, ensemble_map, ensemble_map_var_names
        
    
        
        
