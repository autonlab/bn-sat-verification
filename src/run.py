import logging
import os
from scripts.convert_to_shih import convert_to_shih
from convert_net_to_odd import run_conversion
from odd_parser import read_obdd_from_file
from utils.draw_diagram import draw_obdd
from tseitin_encoding import TseitinEncoder

DATASET_NAME = "darpatriage"
VARS = 11
DATASET_ROOT = "Delayed"
LEAVES = ["Breathless", 
            "EventType", 
            "PerfusionCondition", 
            "RespiratoryCondition", 
            "MentalResponsiveness",
            "BrokenLeg",
            "SkullFracture",
            "BlastInjury",
            "RespiratoryRate",
            "BloodPressure",
            "TorsoDetected"
            ]
RESULTS_DIR = f"results/{DATASET_NAME}"

DATASET_CONFIG = {
    "id": DATASET_ROOT,
    "name": DATASET_NAME,
    "filetype": "net",
    "vars": 11,
    "root": DATASET_ROOT,
    "leaves": LEAVES,
    "threshold": 0.5000001,
    "input_filepath": "../bnc_networks/",
    "output_filepath": "../odd_models/"
}

def run_xsdl_to_net(dataset_name: str) -> bool:
    '''
    Converts the xsdl file to a net file
    '''
    xsdl_file = f"models/{dataset_name}.xdsl"
    net_file = f"bnc_networks/{dataset_name}.net"
    
    convert_to_shih(xsdl_file, net_file)
    
    # Check if net file exists
    if not os.path.exists(net_file):
        logging.error(f"Failed to convert xsdl file to net file")
        return False
    
    logging.info(f"Converted xsdl file to net file")
    return True
    
def run_net_to_odd_compilation(dataset_name: str, json_config: dict) -> bool:
    '''
    Converts the net file to a json config file and compiles it to an OBDD
    '''
    net_file = f"bnc_networks/{dataset_name}.net"
    
    # Check if net file exists
    if not os.path.exists(net_file):
        logging.error(f"Net file {net_file} does not exist")
        return False

    # Run conversion
    run_conversion(json_config)
    
    # Check if OBDD file exists
    obdd_file = f"odd_models/{dataset_name}_{json_config['id']}.odd"
    if not os.path.exists(obdd_file):
        logging.error(f"MDD file {obdd_file} does not exist")
        return False
    
    logging.info(f"Converted net file to OBDD file")
    return True

def run_plot_odd(odd_filename: str, display_block: bool = True, save_path: str = None) -> None:
    '''
    Plots the OBDD
    '''
    mdd = read_obdd_from_file(odd_filename)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    draw_obdd(mdd, odd_filename, display_block=display_block, save_path=save_path)
    logging.info(f"Plotted OBDD and saved to {save_path}")

def run_encoding(odd_filename: str, cnf_save_filename: str) -> None:
    '''
    Runs the Tseitin encoding
    '''
    mdd = read_obdd_from_file(odd_filename)
    encoder = TseitinEncoder()
    cnf, _, _, = encoder.encode_to_cnf(mdd)
    logging.info(f"CNF conversion completed and generated: {len(cnf.clauses)} clauses")
    
    encoder.save_to_json(cnf_save_filename)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s: %(message)s', datefmt="%Y-%m-%d|%H:%M:%S")

    logging.info(f"DATASET_NAME: {DATASET_NAME}")
    logging.info(f"RESULTS_DIR: {RESULTS_DIR}")

    # Check if cwd is src
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create results directory if it doesn't exist
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        logging.info(f"Created directory {RESULTS_DIR}")
        
        
    run_xsdl_to_net(DATASET_NAME)
    
    run_net_to_odd_compilation(DATASET_NAME, DATASET_CONFIG)
    
    odd_filename = f"odd_models/{DATASET_NAME}_{DATASET_ROOT}.odd"
    save_path = f"{RESULTS_DIR}/{DATASET_NAME}/{DATASET_NAME}_{DATASET_ROOT}.png"
    run_plot_odd(odd_filename=odd_filename, save_path=save_path, display_block=False)
    
    cnf_filename = f"cnf_files/{DATASET_NAME}_{DATASET_ROOT}.cnf"
    run_encoding(odd_filename=odd_filename, cnf_save_filename=cnf_filename)
