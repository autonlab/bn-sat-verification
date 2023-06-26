import logging
import argparse
import json

from verifications.verification_case import VerificationCase
from verifications.verification_monotonicity import VerificationCaseBinaryMonotonicity
from verifications.pysat_solver import PySATSolver
from utils.draw_diagram import draw_obdd
import odd_parser
from utils.cnf_json_parser import read_cnf_from_json

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run verifications')
    parser.add_argument('--files', 
                        type=str, 
                        help='Path to the CNF json files and expected results. \
                                Example: --files test1.json:GPA:True,test2.json:GPA:False\
                                Format: <file_name>:<variable_to_verify>:<expected_result>,<file_name>:<variable_to_verify>:<expected_result>, ...',
                        required=True)
    parser.add_argument('--draw', type=str, help='Draw MDD on the file .odd. Filepath: odd_models/<filepath>', default='')
    
    files = [f.split(':') for f in parser.parse_args().files.split(',')]
    files = {f[0]:(f[1], eval(f[2]))for f in files}
    
    print(files)
    
    logging.basicConfig(level=logging.INFO)
    
    for file, (var, expected_result) in files.items():
        cnf, _map_inv, _map, _map_name_vars = read_cnf_from_json(f'cnf_files/{file}')
        solver = PySATSolver()
        
        verif_case = VerificationCaseBinaryMonotonicity(name=f'TestBinaryMonotonicityTask_{var}_should_be_{expected_result}')
        result = verif_case.verify(cnf=cnf,
                            map=_map,
                            sat_solver=solver,
                            variable_to_verify=var,
                            map_name_vars=_map_name_vars)
        
        with open(f'verifications/results/verifications_results{file}_{var}_{expected_result}.json', 'w') as f:
            save = {
                'file': file,
                'variable_to_verify': var,
                'expected_result': expected_result,
                'result': result,
                'SAT_model': verif_case.sat_model,
            }
            json.dump(save, f, indent=4)
        
        print(f'Verification result: {result}')
        assert result == expected_result, f'Verification result for {file} should be {expected_result}'
        
        
        draw_path = parser.parse_args().draw
        
        if draw_path != '':
            mdd = odd_parser.read_obdd_from_file(f'odd_models{draw_path}')
            highlight = {_map_inv[str(x)]: 'r' for x in verif_case.sat_model if x > 0 and str(x) in _map_inv}
            print(highlight)
            draw_obdd(mdd, highlight, title='MDD breaking the monotonicity', display_block=False)
            
            # Second MDD
            cutoff = int(max(_map_inv.keys(), key=lambda x: int(x)))
            second_model = [int(x)-cutoff for x in verif_case.sat_model if int(x) > cutoff]
            highlight2 = {_map_inv[str(x)]: 'r' for x in second_model if x > 0 and str(x) in _map_inv}
            draw_obdd(mdd, highlight2, title='MDD breaking the monotonicity')
        
    