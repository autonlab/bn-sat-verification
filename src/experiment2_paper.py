from run_experiments_binary import ExperimentRunner
import json
import os

result_dict = {
    'ITR_SAT': [],
    'ITR_UNSAT': [],
    'FMO_SAT': [],
    'FMO_UNSAT': [],
    'TOTAL_ITR_TIME': [],
    'TOTAL_FMO_TIME': [],
    'TOTAL_ITR_TIME_PER_QUERY': [],
    'TOTAL_FMO_TIME_PER_QUERY': [],
}

for i, path in enumerate([f'/home/ignacy/cmu/bnc-formal-verification/src/bnc_configs/credit10k_{i}.json' for i in range(10)]):
    with open(path, 'r') as f:
        config = json.load(f)
    
    name = config['name']
    id = config['id']
    
    runner = ExperimentRunner(name, id, logging_level='info')
    runner.run(measure_time=True)
    times = runner.get_times()
    fmo_time = times['fmo'] if times['fmo'] else -1
    itr_time = times['itr'] if times['itr'] else -1
    if fmo_time is not None:
        print(f'Finished {name}_{id} in {fmo_time + itr_time:.0f} ms. Where FMO took {fmo_time:.0f} ms and ITR took {itr_time:.0f} ms.')
    
    ifthen_results_path = os.path.join(runner.artifacts_path, f'ifthen_{name}.json')
    ifthen_results = json.load(open(ifthen_results_path, 'r'))
    itr_unsat_count = 0
    itr_all_count = 0
    for _, result in ifthen_results.items():
        if bool(result['is_UNSAT']):
            itr_unsat_count += 1
        itr_all_count += 1
        
    print(f'ITR_UNSAT: {itr_unsat_count}, ITR_SAT: {itr_all_count - itr_unsat_count}')
    
    fmo_results_path = os.path.join(runner.artifacts_path, f'fmo_{name}.json')
    fmo_results = json.load(open(fmo_results_path, 'r'))
    fmo_unsat_count = 0
    fmo_all_count = 0
    for _, result in fmo_results.items():
        if bool(result['is_UNSAT']):
            fmo_unsat_count += 1
        fmo_all_count += 1
    
    
    result_dict['ITR_SAT'].append(itr_all_count - itr_unsat_count)
    result_dict['ITR_UNSAT'].append(itr_unsat_count)
    result_dict['FMO_SAT'].append(fmo_all_count - fmo_unsat_count)
    result_dict['FMO_UNSAT'].append(fmo_unsat_count)
    result_dict['TOTAL_ITR_TIME'].append(itr_time)
    result_dict['TOTAL_FMO_TIME'].append(fmo_time)
    result_dict['TOTAL_ITR_TIME_PER_QUERY'].append(itr_time / itr_all_count)
    result_dict['TOTAL_FMO_TIME_PER_QUERY'].append(fmo_time / itr_all_count)
    
print(result_dict)