import os
import json

def get_dir() -> str:
    # Change path to directory of this file
    dirpath = os.path.dirname(os.path.abspath(__file__))
    srcpath = os.path.dirname(dirpath)
    dirpath = os.path.join(srcpath, 'BNC_SDD')
    return dirpath

def save_config(filename: str,
                vars: int, 
                root: str, 
                leaves: list = [], 
                threshold: float = 0.5, 
                input_filepath: str = "networks/binarynetworks/", 
                output_filepath: str = "output") -> str:
    '''
    Save a config file that is used by the SDD library to read in the network.
    
    Parameters: 
        filename (str): Name of the config file with extension e.g. "config.json"
        vars (int): Number of variables in the network
        root (str): Name of the root node e.g. "Alarm"
        leaves (list): List of names of the leaf nodes
        threshold (float): Decision threshold for the leaf nodes
        input_filepath (str): Path to the input file directory
        output_filepath (str): Path to the output file directory
    '''
    dirpath = get_dir()
    config = {
        "id": "1",
        "name": filename.split('.')[0],
        "filetype": "net",
        "vars": vars,
        "root": root,
        "leaves": leaves,
        "threshold": threshold,
        "input_filepath": input_filepath,
        "output_filepath": output_filepath
    }

    with open(os.path.join(dirpath, 'config.json'), 'w') as f:
        json.dump(config, f, indent=4)

def save_config(_json: dict) -> str:
    '''
    Save a config file that is used by the BNC_SDD library to read in the network.
    JSON MUST BE IN CORRECT FORMAT
    
    Parameters: 
        json (str): String of the json file
    '''
    dirpath = get_dir()
    with open(os.path.join(dirpath, 'config.json'), 'w') as f:
        json.dump(_json, f, indent=4)

def run_bnc_to_obdd() -> None:
    '''Run the bash file that initializes necessary stuff for the BNC to OBDD conversion'''
    current_cwd = os.getcwd()
    
    dirpath = get_dir()
    os.chdir(dirpath)
    os.system('bash run')
    
    subpath = os.path.join(os.getcwd(), 'src', 'sdd')
    os.chdir(subpath)
    
    # Change cwd back to original
    os.chdir(current_cwd)
