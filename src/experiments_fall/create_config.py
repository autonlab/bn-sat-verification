import json
import os


DATASET_NAME = 'credit10k'
NETWORK_NAME = 'CreditWorthiness'


config_filename = f'{DATASET_NAME}_{NETWORK_NAME}_config.json'
path = os.path.join(os.path.dirname(__file__), config_filename)

config = {
    'network_name': NETWORK_NAME,
    'experiment_n': 1,
    'outcomes': ['CreditWorthiness'],
    'cnf_filepath': f"cnf_files/{DATASET_NAME}_{NETWORK_NAME}.json",
    'OCC': False,
    'FMO': [
        # {'assumptions': [], 'variable_to_verify': 'CVP',},
        ],
    'SEC': [
        # {'if-tuples': [('CVP', 2), ('PCWP', 2)], 'then': ('Y', '>=', 0), }
    ]
}


# Open rules file
rules_filename = f'rules_{DATASET_NAME}.json'
with open(os.path.join(os.path.dirname(__file__), rules_filename), 'r') as f:
    rules = json.load(f)
    
# Add rules to 'SEC' in config
for rule in rules:
    tmp = {}
    tmp['if-tuples'] = rule['rule']
    c = rule['class']
    tmp['then'] = ('Y', '<=', c) if c == 0 else ('Y', '>=', c)
    config['SEC'].append(tmp)


with open(path, 'w') as f:
    json.dump(config, f, indent=4)
