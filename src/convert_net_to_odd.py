import argparse
import json
import os 
import logging
import adapter

def run_conversion(_json: dict) -> None:
    '''
    Run the conversion from BNC to OBDD
    
    Parameters:
        configpath (str): Path to the BNC json config file e.g. bnc_configs/admission.json
    ''' 
    adapter.save_config(_json)
    
    adapter.run_bnc_to_obdd()
    
def copy_net_to_target_dir(filepath: str, target_dir: str) -> None:
    '''
    Copy the network file to the target directory
    
    Parameters:
        filepath (str): Path to the network file e.g. networks/binarynetworks/admission.json
    '''
    os.makedirs(f'BNC_SDD/{target_dir}', exist_ok=True)
    
    logging.debug(f'Copying {filepath} to BNC_SDD/{target_dir}')
    
    os.system(f'cp {filepath} BNC_SDD/{target_dir}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run conversion from BNC to OBDD')
    parser.add_argument('--netfilepath', type=str, help='The filename with path of the BNC to be converted')
    parser.add_argument('--netconfigpath', type=str, help='The filename with path of the BNC config')
    parser.add_argument('--verbose', action='store_true', help='Print debug messages')
    
    if parser.parse_args().verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    filepath = parser.parse_args().netfilepath
    configpath = parser.parse_args().netconfigpath
    
    if not filepath.endswith('.net'):
        filepath += '.net'
    if not configpath.endswith('.json'):
        configpath += '.json'
        
    with open(configpath, 'r') as f:
        _json = json.load(f)
        
    logging.debug(f'Config: {_json}')
    
    # copy_net_to_target_dir(filepath, _json['input_filepath'])
    
    logging.debug(f'Converting {filepath}')
    run_conversion(_json)