import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pgmpy
import seaborn as sns
from sklearn.preprocessing import KBinsDiscretizer
import os
import networkx as nx
from pgmpy.estimators import HillClimbSearch, TreeSearch, PC, ExhaustiveSearch, MmhcEstimator
import warnings
import random
from sklearn.metrics import accuracy_score
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator, ExpectationMaximization
from pgmpy.readwrite import NETWriter
import json
import os 
from .experiment_utils import credit_pipeline, fire_pipeline



def prep_data(data_path: str, data: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    if data is None:
        all_data = pd.read_csv(data_path)
    else:
        all_data = data
    train_df, test_df, TARGET_COL = credit_pipeline(all_data, test_split_ratio=0.3)
    print(f'Train shape: {train_df.shape}, Test shape: {test_df.shape}')
    return train_df, test_df, TARGET_COL

# Filter user warnings
warnings.filterwarnings('ignore')

seed = 123
random.seed(seed)
np.random.seed(seed)

def train_model_structure(train_df: pd.DataFrame, target_col: str, sample_size: float = 0.1) -> BayesianNetwork:
   
    adj_blacklist = set()
    _train_data = train_df.sample(frac=sample_size, random_state=seed)
    
    ts = TreeSearch(_train_data, root_node=target_col)
    m = ts.estimate()
    
    
    G = nx.DiGraph()
    G.add_edges_from(m.edges())
    adj = nx.adjacency_matrix(G).todense()
    if str(adj) not in adj_blacklist:
        adj_blacklist.add(str(adj))
            
        p = m.get_parents(target_col)
        print(f'Parents of {target_col}: {p}')
        if len(p) == 0: # no parents
            return m
        
    return None

def plot_model(model: BayesianNetwork) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    G = nx.DiGraph()
    G.add_edges_from(model.edges())
    pos = nx.spring_layout(G)
    nx.draw(G, 
            pos, 
            with_labels=True,
            node_size=200,
            node_color="skyblue"
            )
    plt.tight_layout()
    plt.show()
    
def estimate_model(model: BayesianNetwork, train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str) -> tuple[BayesianNetwork, float]:
    _train_df = train_df.copy()
        
    # Learing CPDs using Maximum Likelihood Estimators
    model = BayesianNetwork(model.edges())
    
    def get_estimator():
        return MaximumLikelihoodEstimator

    model.fit(_train_df, estimator=get_estimator())
    

    X_test = test_df.drop(target_col, axis='columns')
    ypred = model.predict(X_test)
    test_acc = accuracy_score(test_df[target_col], ypred[target_col])
    print(f'Accuracy on test data: {test_acc} for model')
    
    return model, test_acc

def save_model(dirpath: str, model: BayesianNetwork, id: int, target_col: str, vars_count: int) -> str:
    '''
    Saves models to file and returns list of paths to saved models
    '''

    src_path = os.path.dirname(dirpath)
    print(src_path)

    paths = []
    
    # Create directories if they don't exist
    if not os.path.exists(f'{src_path}/bnc_networks/'):
        os.makedirs(f'{src_path}/bnc_networks/', mode=0o777)
    if not os.path.exists(f'{src_path}/bnc_configs/'):
        os.makedirs(f'{src_path}/bnc_configs/', mode=0o777)
    if not os.path.exists(f'{dirpath}/models/'):
        os.makedirs(f'{dirpath}/models/', mode=0o777)

    # Save model
    NETWriter(model).write_net(f'{dirpath}/models/credit10k_{id}.net')
    NETWriter(model).write_net(f'{src_path}/bnc_networks/credit10k_{id}.net')

    DATASET_CONFIG = {
        "id": id,
        "name": 'credit10k',
        "filetype": "net",
        "vars": vars_count,
        "root": target_col,
        "leaves": 6,
        "threshold": 0.5,
        "input_filepath": "../bnc_networks/",
        "output_filepath": "../odd_models/"
    }

    s = f'{src_path}/bnc_configs/credit10k_{id}.json'
    paths.append(s)
    with open(s, 'w') as f:
        json.dump(DATASET_CONFIG, f, indent=4)
            
    return paths


if __name__ == '__main__':
    
    
    
    filedirpath = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(filedirpath, 'data/credit10k.csv')
    
    train_df, test_df, target_col = prep_data(data_path)
    
    model = train_model_structure(train_df, target_col)
    plot_model(model)
    trained_model, test_accuracy = estimate_model(model, train_df, test_df, target_col)
    print(f'Test accuracy: {test_accuracy}')
    
    save_model(filedirpath, trained_model, 999, target_col, train_df.shape[1])
    
    
    
        