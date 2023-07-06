import logging
import os
import json

from pysat.formula import CNF

from verifications.pysat_solver import PySATSolver
from verifications.verification_class_coherency import VerificationCaseClassCoherency
from verifications.verifiaction_experiment import VerificationExperiment

dirpath = os.path.dirname(os.path.abspath(__file__))

DATASET_NAME = "darpatriage"
CNF_FILEPATH = f"cnf_files/{DATASET_NAME}_ensemble.json"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    with open(os.path.join(dirpath, CNF_FILEPATH), 'r') as f:
        data = json.load(f)
        
    sinks_map = data['sinks_map']
    _map = data['map']
    cnf = CNF(from_clauses=data['cnf'])
    sat_solver = PySATSolver()
    
    
    sinks_names_in_order = []
    for filename, sinks in sinks_map.items():
        sinks_names_in_order.append((sinks[0], sinks[1]))
        
    sinks_names_in_order = sorted(sinks_names_in_order, 
                                  key=lambda x: int(x[0].split('__')[1]) if '__' in x[0] else -1)
        
    case1 = VerificationCaseClassCoherency(name='All Class Coherency', 
                                            map=_map, 
                                            sink_names_in_order=sinks_names_in_order,
                                            # only_check_sinks=None
                                            )
                                           
    
    experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
    experiment.add_verification_case(case1)
    experiment.run_all_verification_cases()
    
    
    
