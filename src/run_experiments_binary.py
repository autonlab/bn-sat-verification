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


    
def translate_results(results: dict, inv_map: dict) -> dict:
    '''
    Translate results from pysat solver to human-readable format
    '''
    
    def __translate_model(model: list) -> list:
        true_elements = []
        false_elements = []
        
        if model is not None:
            for atom in model:
                sign = 1 if atom > 0 else -1
                atom = str(abs(atom))
                if sign == 1:
                    true_elements.append(inv_map[atom])
                else:
                    false_elements.append(inv_map[atom])
                    
        return true_elements, false_elements
    
    for key, value in results.items():
        model = value['result_model']
        
        true_elements, false_elements = __translate_model(model)
        results[key]['true_variables'] = true_elements
        results[key]['false_variables'] = false_elements
        
        
        _all_sat_models = value['all_sat_models'].copy()
        
        results[key]['all_sat_models'] = []
        for sat_model in _all_sat_models:
            true_elements, false_elements = __translate_model(sat_model)
            results[key]['all_sat_models'] += [{'true_variables': true_elements, 'false_variables': false_elements}]

    return results
    
   

class ExperimentRunner:
    
    def __init__(self, 
                 dataset_name: str,
                 id: int,
                 experiments_path = 'experiments_fall',
                 logging_level: str = 'info',
                 nofmo: bool = False,
                 noitr: bool = False,
                 ) -> None:
        '''
        dataset_name: name of the dataset
        id: id from the config file
        logging_level: logging verbosity level, e.g., 'info', 'debug', 'warning'
        nofmo: don't run FMO verification queries
        noitr: don't run ITR verification queries
        '''
        
        self.dataset_name = dataset_name
        self.id = id
        self.logging_level = logging_level
        self.nofmo = nofmo
        self.noitr = noitr
        self.experiments_path = experiments_path
        
        self.itr_time = None
        self.fmo_time = None
        
        self.setup()
        
    def setup(self) -> None:
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.artifacts_path = os.path.join( self.dirpath, self.experiments_path, f'{self.dataset_name}_{self.id}_artifacts')
        if not os.path.exists(self.artifacts_path):
            os.makedirs(self.artifacts_path)
            
        self.config_path = os.path.join( self.dirpath, self.experiments_path, f'{self.dataset_name}_{self.id}_config.json')
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
        self.experiment_n = self.config['experiment_n'] # average over n runs
        self.binary = True if len(self.config['outcomes']) == 1 else False
        assert self.binary is True, 'Only binary case is supported!!'
        
        self.verbose = self.logging_level
        match self.verbose:
            case 'debug':
                self.verbose = logging.DEBUG
            case 'info':
                self.verbose = logging.INFO
            case 'warning':
                self.verbose = logging.WARNING
                
        logging.basicConfig(level=self.verbose, format='%(asctime)s|%(levelname)s: %(message)s', datefmt="%Y-%m-%d|%H:%M:%S")

        with open(os.path.join( self.dirpath, self.config['cnf_filepath']), 'r') as f:
            self.data = json.load(f)
        
        self.map = self.data['map']
        self.inv_map = self.data['map_inv']
        self.cnf = CNF(from_clauses=self.data['cnf'])
        self.sat_solver = PySATSolver()
        sinks_map = self.data['sinks_map']
        
        # Sort sinks in order
        self.sinks_names_in_order = [None] * len(sinks_map)
        for _, sinks in sinks_map.items():
            if 'TRUE' in sinks[0]:
                self.sinks_names_in_order[0] = (sinks[0], sinks[1])
            else:
                self.sinks_names_in_order[0] = (sinks[1], sinks[0])
        
        
        
    def fmo(self, iterate_sat_models: bool = False) -> None:
        experiment = VerificationExperiment(cnf=self.cnf, sat_solver=self.sat_solver)
        for i, case in enumerate(self.config['FMO']):
            assumptions, variable_to_verify = case.values()
            
            fmo_verif = VerificationCaseMulticlassMonotonicity(name=f'{variable_to_verify}-Monotonicity',
                                                            map=self.map,
                                                            sink_names_in_order=self.sinks_names_in_order,
                                                            variable_to_verify=variable_to_verify,
                                                            map_name_vars=self.data['map_names_vars'],
                                                            assumptions=assumptions,
                                                            binary=self.binary
                                                        )
            
            
            
            experiment.add_verification_case(fmo_verif)
        experiment.run_all_verification_cases()
            
    def itr(self, iterate_sat_models: bool = True) -> None:
        
        experiment = VerificationExperiment(cnf=self.cnf, sat_solver=self.sat_solver)
        
        for i, case in enumerate(self.config['ITR']):
            if_tuples, then = case.values() 
            
            # Remove tuples that involve irrelevant variable
            filtered_tuples = list()
            for tpl in if_tuples:
                if any(str(tpl[0]).lower() in s.lower() for s in self.map.keys()):
                  filtered_tuples.append(tpl)  
            
            verif = VerificationIfThenRules(
                name=f'IfThen#{i}',
                map=self.map,
                sink_names_in_order=self.sinks_names_in_order,
                if_tuples=filtered_tuples,
                then_tuples=[then], 
                map_name_vars=self.data['map_names_vars'],
                binary=self.binary
            )
            
            experiment.add_verification_case(verif)
            
        experiment.run_all_verification_cases(generate_all_SAT_models=iterate_sat_models)
        results = translate_results(experiment.results, self.inv_map)
            
        with open(os.path.join(self.artifacts_path, f'ifthen_{self.dataset_name}.json'), 'w') as f:
            json.dump(results, f, indent=4)
            
    def run(self, measure_time: bool = True) -> None:
        
        if measure_time:
            # FMO
            if not self.nofmo:
                runtime = timeit.timeit(self.fmo, number=self.experiment_n) / self.experiment_n
                logging.debug(f'FMO: Average time: {runtime*1000:.2f} ms')
                self.fmo_time = runtime * 1000
            
            # ITR
            if not self.noitr:
                runtime = timeit.timeit(self.itr, number=self.experiment_n) / self.experiment_n
                logging.debug(f'ITR: Average time: {runtime*1000:.2f} ms')
                self.itr_time = runtime * 1000
        else:
            if not self.nofmo:
                self.fmo()
            if not self.noitr:
                self.itr()
                
    def get_times(self) -> tuple:
        return {'fmo': self.fmo_time, 'itr': self.itr_time}


if __name__ == '__main__':
    pass



