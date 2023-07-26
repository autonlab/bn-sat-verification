import logging
import os
import json

from pysat.formula import CNF

from verifications.pysat_solver import PySATSolver
from verifications.verification_class_coherency import VerificationCaseClassCoherency
from verifications.verifiaction_experiment import VerificationExperiment
from verifications.verification_multiclass_monotonicity import VerificationCaseMulticlassMonotonicity
from verifications.verification_ifthen import VerificationIfThenRules

dirpath = os.path.dirname(os.path.abspath(__file__))

DATASET_NAME = "triage_monotonic"
CLASS_ORDER = ['Class']
VARIABLE_TO_VERIFY = 'BreathingRateConfidence'
CNF_FILEPATH = f"cnf_files/{DATASET_NAME}_ensemble.json"

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    with open(os.path.join(dirpath, CNF_FILEPATH), 'r') as f:
        data = json.load(f)
        
    sinks_map = data['sinks_map']
    _map = data['map']
    cnf = CNF(from_clauses=data['cnf'])
    sat_solver = PySATSolver()
    
    
    sinks_names_in_order = [None] * len(sinks_map)
    
    for filename, sinks in sinks_map.items():
        for i, _class in enumerate(CLASS_ORDER):
            if _class in filename:
                if 'TRUE' in sinks[0]:
                    sinks_names_in_order[i] = (sinks[0], sinks[1])
                else:
                    sinks_names_in_order[i] = (sinks[1], sinks[0])
        
        
    # sinks_names_in_order = sorted(sinks_names_in_order, 
                                #   key=lambda x: int(x[0].split('__')[1]) if '__' in x[0] else -1)
        
    # case1 = VerificationCaseClassCoherency(name='All Class Coherency', 
    #                                         map=_map, 
    #                                         sink_names_in_order=sinks_names_in_order,
    #                                         # only_check_sinks=None
    #                                         )
                                           
    
    # experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
    # experiment.add_verification_case(case1)
    # experiment.run_all_verification_cases()
    
    
    case2 = VerificationCaseMulticlassMonotonicity(name=f'{VARIABLE_TO_VERIFY}-Monotonicity',
                                                    map=_map,
                                                    sink_names_in_order=sinks_names_in_order,
                                                    variable_to_verify=VARIABLE_TO_VERIFY,
                                                    map_name_vars=data['map_names_vars'],
                                                    binary=True
                                                   )
    
    cnf = CNF(from_clauses=data['cnf'])
    
    
    experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
    experiment.add_verification_case(case2)
    experiment.run_all_verification_cases()
    
    
    # case3 = VerificationIfThenRules(
    #     name=f'{VARIABLE_TO_VERIFY}-IfThen',
    #     map=_map,
    #     sink_names_in_order=sinks_names_in_order,
    #     if_tuples=[('PulseRate', 1), ('PulseRateConfidence', 2), ('BreathingRate', 1), ('BreathingRateConfidence', 3)],
    #     then_tuples=[('Y', '>=', 1)], 
    #     map_name_vars=data['map_names_vars'],
    #     binary=True
    # )
    # cnf = CNF(from_clauses=data['cnf'])
    # experiment = VerificationExperiment(cnf=cnf, sat_solver=sat_solver)
    # experiment.add_verification_case(case3)
    # experiment.run_all_verification_cases()
    
    
    
    
