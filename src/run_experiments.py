import logging
import os
import json
import timeit
import argparse

from pysat.formula import CNF

from verifications.pysat_solver import PySATSolver
from verifications.verification_class_coherency import VerificationCaseClassCoherency
from verifications.verifiaction_experiment import VerificationExperiment
from verifications.verification_multiclass_monotonicity import VerificationCaseMulticlassMonotonicity
from verifications.verification_ifthen import VerificationIfThenRules


EXPERIMENTS_PATH = 'experiments_fall'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run compilation&encoding pipeline')
    parser.add_argument('--dataset', type=str, help="Dataset name, e.g., --dataset=alarm", required=True)
    parser.add_argument('--ynode', type=str, help="Only for binary case, pass here the name of Y variable, e.g., --ynode=LVFailure", required=True)
    parser.add_argument('--logging', choices=['debug', 'info', 'warning'], help='Logging verbosity level', default='info')
    parser.add_argument('--nofmo', action='store_true', default=False, help="Don't run FMO verification queries")
    parser.add_argument('--nocc', action='store_true', default=False, help="Don't run CC verification queries")
    parser.add_argument('--nosec', action='store_true', default=False, help="Don't run SEC verification queries")

    dirpath = os.path.dirname(os.path.abspath(__file__))

    DATASET_NAME = parser.parse_args().dataset
    Y_NODE_NAME = parser.parse_args().ynode
    
    ARTIFACTS_PATH = os.path.join(dirpath, EXPERIMENTS_PATH, f'{DATASET_NAME}_artifacts')
    if not os.path.exists(ARTIFACTS_PATH):
        os.makedirs(ARTIFACTS_PATH)

    config_path = os.path.join(dirpath, EXPERIMENTS_PATH, f'{DATASET_NAME}_{Y_NODE_NAME}_config.json') 

    with open(config_path, 'r') as f:
        CONFIG = json.load(f)
        
    EXPERIMENT_N = CONFIG['experiment_n'] # average over n runs

    BINARY = True if len(CONFIG['outcomes']) == 1 else False 
    print(f'Binary: {BINARY}')


    verbosity_level = parser.parse_args().logging
    if verbosity_level == 'debug': verbosity_level = logging.DEBUG
    elif verbosity_level == 'info': verbosity_level = logging.INFO
    elif verbosity_level == 'warning': verbosity_level = logging.WARNING

    logging.basicConfig(level=verbosity_level, format='%(asctime)s|%(levelname)s: %(message)s', datefmt="%Y-%m-%d|%H:%M:%S")    
    with open(os.path.join(dirpath, CONFIG['cnf_filepath']), 'r') as f:
        data = json.load(f)
        
    _map = data['map']
    _inv_map = data['map_inv']
    cnf = CNF(from_clauses=data['cnf'])
    sat_solver = PySATSolver()
    
    sinks_map = data['sinks_map']
    
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
    if CONFIG['OCC'] is True and not parser.parse_args().nocc: 
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
    if CONFIG['FMO'] and not parser.parse_args().nofmo:
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
    
    
    def translate_results(results: dict) -> dict:
        
        for key, value in results.items():
            model = value['result_model']
            true_elements = []
            false_elements = []
            
            if model is not None:
                for atom in model:
                    sign = 1 if atom > 0 else -1
                    atom = str(abs(atom))
                    if sign == 1:
                        true_elements.append(_inv_map[atom])
                    else:
                        false_elements.append(_inv_map[atom])
                    
            results[key]['true_variables'] = true_elements
            results[key]['false_variables'] = false_elements

        return results
   
    # IF then Rules (Safety Engineering Constraints)
    if CONFIG['SEC'] and not parser.parse_args().nosec:
        
        def __sec():
            cnf = CNF(from_clauses=data['cnf'])
            experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
            for i, case in enumerate(CONFIG['SEC']):
                if_tuples, then = case.values() 
                verif = VerificationIfThenRules(
                    name=f'IfThen#{i}',
                    map=_map,
                    sink_names_in_order=sinks_names_in_order,
                    if_tuples=if_tuples,
                    then_tuples=[then], 
                    map_name_vars=data['map_names_vars'],
                    binary=BINARY
                )
                experiment.add_verification_case(verif)
            experiment.run_all_verification_cases()
            
            results = translate_results(experiment.results)
            
            with open(os.path.join(ARTIFACTS_PATH, f'ifthen_{DATASET_NAME}.json'), 'w') as f:
                json.dump(results, f, indent=4)
        
         
        runtime = timeit.timeit(__sec, number=EXPERIMENT_N) / EXPERIMENT_N
        logging.debug(f'SEC#{i}: Average time: {runtime*1000:.2f} ms')




