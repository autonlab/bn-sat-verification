import logging

from verifications.verification_case import VerificationCase
from verifications.verification_monotonicity import VerificationCaseBinaryMonotonicity
from verifications.pysat_solver import PySATSolver
from utils.cnf_json_parser import read_cnf_from_json

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    
    files = {
        'test_monotonic_diagram.json': ('GPA', True),
        'test_multival_diagram.json': ('GPA', False),
    }
    
    for file, (var, expected_result) in files.items():
        cnf, _map_inv, _map, _map_name_vars = read_cnf_from_json(f'cnf_files/{file}')
        solver = PySATSolver()
        
        verif_case = VerificationCaseBinaryMonotonicity(name=f'TestBinaryMonotonicityTask_{var}_should_be_{expected_result}')
        result = verif_case.verify(cnf=cnf,
                            map=_map,
                            sat_solver=solver,
                            variable_to_verify=var,
                            map_name_vars=_map_name_vars)
        
        print(f'Verification result: {result}')
        assert result == expected_result, f'Verification result for {file} should be {expected_result}'
    