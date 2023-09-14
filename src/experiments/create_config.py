import json
import os


DATASET_NAME = 'alarm'
NETWORK_NAME = 'LVFailure'

config_filename = f'{DATASET_NAME}_{NETWORK_NAME}_config.json'
path = os.path.join(os.path.dirname(__file__), config_filename)

config = {
    'network_name': NETWORK_NAME,
    'experiment_n': 1,
    'outcomes': ['LVFailure'],
    'cnf_filepath': f"cnf_files/{DATASET_NAME}_{NETWORK_NAME}.json",
    'OCC': True,
    'FMO': [
        {'assumptions': [], 'variable_to_verify': 'CVP',},
        ],
    'SEC': [
        {'if-tuples': [('CVP', 2), ('PCWP', 2)], 'then': ('Y', '>=', 0), }
    ]
}

with open(path, 'w') as f:
    json.dump(config, f, indent=4)
