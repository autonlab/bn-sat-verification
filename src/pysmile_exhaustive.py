import logging
import os
import json
import timeit
import numpy as np
import scripts.pysmile_license
import pysmile
from scripts.pysmile_utils import *


dirpath = os.path.dirname(os.path.abspath(__file__))

XDSL_MODEL_PATH = 'models'
EXPERIMENTS_PATH = 'experiments'
DATASET_NAME = "darpatriage"

model_path = os.path.join(dirpath, XDSL_MODEL_PATH, f'{DATASET_NAME}.xdsl')
config_path = os.path.join(dirpath, EXPERIMENTS_PATH, f'{DATASET_NAME}_config.json') 

with open(config_path, 'r') as f:
    CONFIG = json.load(f)
    
CONFIG['outcomes'] = {k for k in CONFIG['outcomes']}


def class_coherency(net: pysmile.Network):
    search_parameters = []
    search_grid = []
    outcomes = CONFIG['outcomes']
    
    
    # prep
    for node_id in net.get_all_nodes():
        name = net.get_node_name(node_id)
        values = net.get_outcome_ids(node_id)
        
        logging.debug(f'{net.get_node_name(node_id)}: {net.get_outcome_ids(node_id)}')
        
        if name not in CONFIG['outcomes']:
            search_parameters.append((name, values))
            search_grid.append([i for i in range(len(values))])
    
    # TODO: FIX
    search_grid = np.meshgrid(np.array(search_grid)) 
    print(search_grid)
    
    # exhaustive search in parameter space
    
        
        
        
if __name__ == '__main__':
    _net = pysmile.Network()
    _net.read_file(model_path)
    _net.update_beliefs()
    
    
    logging.basicConfig(level=logging.DEBUG)
    
    
    class_coherency(_net)
