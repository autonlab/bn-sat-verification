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
            
        # Add FMOs to 'FMO' in config
        fmo_filename = f'{DATASET_NAME}_fmo.json'
        with open(os.path.join(os.path.dirname(__file__), fmo_filename), 'r') as f:
            fmo = json.load(f)
            
        config['FMO'] = fmo


        with open(path, 'w') as f:
            json.dump(config, f, indent=4)
            
        paths.append(path)

    return paths


def create_custom(
    dataset_name: str,
    id: int,
    outcomes: list,
    fmo: list[dict],
    itr: list[dict]
):
    config = {
        'dataset': dataset_name,
        'id': id,
        'experiment_n': 1,
        'outcomes': [outcomes],
        'config_filepath': f"bnc_configs/{dataset_name}_{id}.json",
        'cnf_filepath': f"cnf_files/{dataset_name}_{id}.json",
        'OCC': False,
        'FMO': fmo,
        'ITR': itr
    }
    
    config_filename = f'{dataset_name}_{id}_config.json'
    path = os.path.join(os.path.dirname(__file__), config_filename)
    
    with open(path, 'w') as f:
        json.dump(config, f, indent=4)


if __name__ == '__main__':
    create('credit10k', [999])