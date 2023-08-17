import json
import os


NETWORK_NAME = 'darpatriage'

config_filename = f'{NETWORK_NAME}_config.json'
path = os.path.join(os.path.dirname(__file__), config_filename)

config = {
    'network_name': NETWORK_NAME,
    'experiment_n': 50,
    'outcomes': ['Minimal', 'Delayed', 'Immediate'],
    'cnf_filepath': f"cnf_files/{NETWORK_NAME}_ensemble.json",
    'OCC': True,
    'FMO': [
        {'assumptions': [('Breathless', 0), ('BlastInjury', 1)], 'variable_to_verify': 'RespiratoryRate',},
        {'assumptions': [('Breathless', 0), ('BlastInjury', 0)], 'variable_to_verify': 'RespiratoryRate',},
        {'assumptions': [('TorsoDetected', 1), ('BrokenLeg', 1)], 'variable_to_verify': 'BloodPressure',},
        {'assumptions': [('TorsoDetected', 0), ('BrokenLeg', 1)], 'variable_to_verify': 'BloodPressure',},
        ],
    'SEC': [
        {'if-tuples': [('Breathless', 0), ('BlastInjury', 1)], 'then': ('Y', '>=', 1), },
        {'if-tuples': [('Breathless', 0), ('BlastInjury', 1)], 'then': ('Y', '<=', 0), },
        {'if-tuples': [('Breathless', 0), ('BlastInjury', 1)], 'then': ('Y', '>=', 0), }
    ]
}

with open(path, 'w') as f:
    json.dump(config, f, indent=4)
