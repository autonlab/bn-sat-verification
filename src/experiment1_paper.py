import json
import timeit
import os
import random
import logging
import pandas as pd

from run import run_net_to_odd_compilation, run_encoding, test_if_cnf_satisfiable, read_cnf_from_json, run_plot_odd
from experiments_fall.create_config import create_custom
from run_experiments_binary import ExperimentRunner

# logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s: %(message)s', datefmt="%Y-%m-%d|%H:%M:%S")

os.chdir('src')
random.seed(421)

successful_compilations = []

compilation_times = []
encoding_times = []
verification_times = []


TIMEIT_REPEATS = 10

base_path = 'bnc_configs/'
config_paths = [
    'admission.json',
    'asia.json',
    'child.json',
    'alarm.json',
    'win95pts.json',
]

def generate_random_itr(n: int, varnames: list):
    itrs = []
    
    signs = ['>=', '<=', '>', '<']
    vals = [0,1]
    conds = [1,2,3,4,5]
    thens = [
        ('Y', '<=', 0),
        ('Y', '>=', 1),
    ]
    
    for i in range(n):
        itrs.append({
            'if-tuples': [(random.choice(varnames), random.choice(signs), random.choice(vals)) for _ in range(random.choice(conds))],
            'then': random.choice(thens)
        })
    
    return itrs

def generate_random_fmo(n: int, varnames: list):
    fmos = []

    vals = [0,1]
    assumptions = [3,4,5,6,7]
    
    for i in range(n):
        
        _varnames = varnames.copy()
        random.shuffle(_varnames)
        
        variable_to_verify = _varnames[0]
        assumption_vars = _varnames[1:random.choice(assumptions)]
        
        fmos.append({
            'assumptions': [[v, random.choice(vals)] for v in assumption_vars],
            'variable_to_verify': variable_to_verify
        })
        
    return fmos
        
def get_varnames_from_odd(odd_filename: str):
    with open(odd_filename, 'r') as f:
        line = f.readline()
    
    line = line.replace(' ', '')
    line = line.replace('[', '')
    line = line.replace(']', '')
    varnames = line.split(',')
    varnames = [v.strip() for v in varnames]
    
    return varnames
    

for path in config_paths:
    path = base_path + path
    with open(path, 'r') as f:
        config = json.load(f)
    
    name = config['name']
    id = config['id']
    config['leaves'] = []
    def __compile():
        return run_net_to_odd_compilation(name, config)
    
    print(f'Starting {name}_{id}')  
    
    avg_comp_time = timeit.timeit(__compile, number=TIMEIT_REPEATS) / TIMEIT_REPEATS
    compilation_times.append(avg_comp_time)
    
    # success = __compile() # Run again to get the result
    # successful_compilations.append(success)
    # print(f'Compilation success: {success}')
    
    # if success:
    odd_filename = f"odd_models/{name}_{id}.odd"
    cnf_filename = f"cnf_files/{name}_{id}.json"
    
    def __enocde():
        run_encoding(odd_filename, cnf_filename)
    
    avg_enc_time = timeit.timeit(__enocde, number=TIMEIT_REPEATS) / TIMEIT_REPEATS
    encoding_times.append(avg_enc_time * 1000)
    
    
    varnames = get_varnames_from_odd(odd_filename)
    print(f'Variable names: {varnames}')
    
    
    queries_count = 20
    
    create_custom(
        dataset_name=name,
        id=id,
        outcomes=config['root'],
        fmo=generate_random_fmo(queries_count // 2, varnames),
        itr=generate_random_itr(queries_count // 2, varnames)
        )
    
    print(name, id)
    er = ExperimentRunner(
        dataset_name = name,
        id = id,
        logging_level='warning',
        )
    
    er.run(measure_time=True)
    
    times = er.get_times()
    verification_times.append({k:v / (queries_count // 2) for k,v in times.items()})
    
    print(f'Finished {name}_{id}')
    
    print(f'Current results:')
    tmp_frame = pd.DataFrame(
        {
            'compilation [s]': compilation_times,
            'encoding [ms]': encoding_times,
            'itr [ms]': [v['itr'] for v in verification_times],
            'fmo [ms]': [v['fmo'] for v in verification_times],
            'avg verification time [ms]': [(v['fmo'] + v['itr']) / 2 for v in verification_times],
        }
    )
    print(tmp_frame)
    
print(f'Successful compilations: {successful_compilations}')
print(f'Compilation times: {compilation_times}')
print(f'Encoding times: {encoding_times}')
print(f'Verification times: {verification_times}')

d = pd.DataFrame(
    {
        'compilation [s]': compilation_times,
        'encoding [ms]': encoding_times,
        'itr [ms]': [v['itr'] for v in verification_times],
        'fmo [ms]': [v['fmo'] for v in verification_times],
        'avg verification time [ms]': [(v['fmo'] + v['itr']) / 2 for v in verification_times],
    }
)
d.index = [c.split('.')[0] for c in config_paths]

# to latex
# d = d.round(2)
d.T.to_latex('experiments_fall/experiment1_Minisat11.tex', float_format="%.2f")
d = d.T.to_latex(float_format="%.2f")

print(d)
