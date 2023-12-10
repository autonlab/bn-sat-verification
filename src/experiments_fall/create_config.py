import json
import os


def create(DATASET_NAME = 'credit10k', IDS = list(range(10))) -> list:
    '''
    Creates config files for each dataset and ID
    '''
    paths = []
    for ID in IDS:
        config_filename = f'{DATASET_NAME}_{ID}_config.json'
        path = os.path.join(os.path.dirname(__file__), config_filename)

        config = {
            'dataset': DATASET_NAME,
            'id': ID,
            'experiment_n': 1,
            'outcomes': ['CreditWorthiness'],
            'config_filepath': f"bnc_configs/{DATASET_NAME}_{ID}.json",
            'cnf_filepath': f"cnf_files/{DATASET_NAME}_{ID}.json",
            'OCC': False,
            'FMO': [
                # {'assumptions': [], 'variable_to_verify': 'CVP',},
                ],
            'ITR': [
                # {'if-tuples': [('CVP', 2), ('PCWP', 2)], 'then': ('Y', '>=', 0), }
            ]
        }


        # Open rules file
        rules_filename = f'rules_{DATASET_NAME}.json'
        with open(os.path.join(os.path.dirname(__file__), rules_filename), 'r') as f:
            rules = json.load(f)
            
        # Add rules to 'ITR' in config
        for rule in rules:
            tmp = {}
            tmp['if-tuples'] = rule['rule']
            c = rule['class']
            tmp['then'] = ('Y', '<=', c) if c == 0 else ('Y', '>=', c)
            config['ITR'].append(tmp)


        with open(path, 'w') as f:
            json.dump(config, f, indent=4)
            
        paths.append(path)

    return paths

if __name__ == '__main__':
    create()