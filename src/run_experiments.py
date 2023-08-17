import logging
import os
import json
import timeit

from pysat.formula import CNF

from verifications.pysat_solver import PySATSolver
from verifications.verification_class_coherency import VerificationCaseClassCoherency
from verifications.verifiaction_experiment import VerificationExperiment
from verifications.verification_multiclass_monotonicity import VerificationCaseMulticlassMonotonicity
from verifications.verification_ifthen import VerificationIfThenRules

dirpath = os.path.dirname(os.path.abspath(__file__))

EXPERIMENTS_PATH = 'experiments'
DATASET_NAME = "darpatriage"

config_path = os.path.join(dirpath, EXPERIMENTS_PATH, f'{DATASET_NAME}_config.json') 

with open(config_path, 'r') as f:
    CONFIG = json.load(f)
    
EXPERIMENT_N = CONFIG['experiment_n'] # average over n runs

BINARY = True if len(CONFIG['outcomes']) == 1 else False 


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    
    with open(os.path.join(dirpath, CONFIG['cnf_filepath']), 'r') as f:
        data = json.load(f)
        
    sinks_map = data['sinks_map']
    _map = data['map']
    cnf = CNF(from_clauses=data['cnf'])
    sat_solver = PySATSolver()
    
    sinks_names_in_order = [None] * len(sinks_map)
    
    for filename, sinks in sinks_map.items():
        for i, _class in enumerate(CONFIG['outcomes']):
            if _class in filename:
                if 'TRUE' in sinks[0]:
                    sinks_names_in_order[i] = (sinks[0], sinks[1])
                else:
                    sinks_names_in_order[i] = (sinks[1], sinks[0])
        
        
    sinks_names_in_order = sorted(sinks_names_in_order, 
                                  key=lambda x: int(x[0].split('__')[1]) if '__' in x[0] else -1)
        
    
    
    # Ordinal Class Coherency
    if CONFIG['OCC'] is True: 
        def __occ():
            coherency_verif = VerificationCaseClassCoherency(name='All Class Coherency', 
                                                    map=_map, 
                                                    sink_names_in_order=sinks_names_in_order,
                                                    # only_check_sinks=None
                                                    )
                                                
            experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
            experiment.add_verification_case(coherency_verif)
            experiment.run_all_verification_cases()
        
        
        runtime = timeit.timeit(__occ, number=EXPERIMENT_N) / EXPERIMENT_N
        print(f'OCC: Average time: {runtime*1000:.2f} ms')
    
    
    # Feature Monotonicity
    if CONFIG['FMO']:
        for i, case in enumerate(CONFIG['FMO']):
            assumptions, variable_to_verify = case.values()
            
            def __fmo():
                fmo_verif = VerificationCaseMulticlassMonotonicity(name=f'{variable_to_verify}-Monotonicity',
                                                                map=_map,
                                                                sink_names_in_order=sinks_names_in_order,
                                                                variable_to_verify=variable_to_verify,
                                                                map_name_vars=data['map_names_vars'],
                                                                assumptions=assumptions,
                                                                binary=BINARY
                                                            )
                
                cnf = CNF(from_clauses=data['cnf'])
                
                
                experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
                experiment.add_verification_case(fmo_verif)
                experiment.run_all_verification_cases()
            
            runtime = timeit.timeit(__fmo, number=EXPERIMENT_N) / EXPERIMENT_N
            print(f'FMO#{i}: Average time: {runtime*1000:.2f} ms')
    
   
    # IF then Rules (Safety Engineering Constraints)
    if CONFIG['SEC']:
        for i, case in enumerate(CONFIG['SEC']):
            if_tuples, then = case.values()
        def __sec():
            verif = VerificationIfThenRules(
                name=f'IfThen#{i}',
                map=_map,
                sink_names_in_order=sinks_names_in_order,
                if_tuples=if_tuples,
                then_tuples=[then], 
                map_name_vars=data['map_names_vars'],
                binary=BINARY
            )
            cnf = CNF(from_clauses=data['cnf'])
            experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
            experiment.add_verification_case(verif)
            experiment.run_all_verification_cases()
            
        runtime = timeit.timeit(__sec, number=EXPERIMENT_N) / EXPERIMENT_N
        print(f'SEC#{i}: Average time: {runtime*1000:.2f} ms')




