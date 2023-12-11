import random
import json
from experiment_utils import credit10k_translation_table


def get_varnames_from_odd(odd_filename: str):
    with open(odd_filename, 'r') as f:
        line = f.readline()
    
    line = line.replace(' ', '')
    line = line.replace('[', '')
    line = line.replace(']', '')
    varnames = line.split(',')
    varnames = [v.strip() for v in varnames]
    
    return varnames

def generate_random_fmo(n: int, varnames: list):
    fmos = []

    vals = {k: sorted([v for _, v in credit10k_translation_table[k].items()]) for k in varnames}
    assumptions = [3,4,5,6,7,8]
    
    vars_with_3_or_more_vals = list(filter(lambda x: len(vals[x]) >= 3, varnames))
    
    for i in range(n):
        _varnames = varnames.copy()
        random.shuffle(_varnames)
        
        # variable_to_verify = random.choice(vars_with_3_or_more_vals)
        variable_to_verify = 'Age'
        
        _varnames.remove(variable_to_verify)
        assumption_vars = _varnames[:random.choice(assumptions)]
        
        fmos.append({
            'assumptions': [[v, random.choice(vals[v])] for v in assumption_vars],
            'variable_to_verify': variable_to_verify
        })
        
    return fmos

if __name__ == '__main__':
    import os
    
    # path = 'odd_models/credit10k_1.odd'
    
    varnames = list(credit10k_translation_table.keys())
    
    # varnames = get_varnames_from_odd(path) + ['CreditWorthiness']
    
    random.seed(32)
    fmos = generate_random_fmo(10, varnames)
    
    
    
    path = os.path.join(os.path.dirname(__file__), 'credit10k_fmo.json')
    
    with open(path, 'w') as f:
        json.dump(fmos, f, indent=4)
    
    print(fmos)