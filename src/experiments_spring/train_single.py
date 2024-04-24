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

print(os.getcwd())

from .experiment_utils import credit_pipeline, fire_pipeline

# make sure that we are in file directory
filedirpath = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(filedirpath, 'data/credit10k.csv')
all_data = pd.read_csv(data_path)

train_df, test_df, TARGET_COL = credit_pipeline(all_data, test_split_ratio=0.3)
print(f'Train shape: {train_df.shape}, Test shape: {test_df.shape}')
# print(train_df.head())

# Filter user warnings
warnings.filterwarnings('ignore')

seed = 123
random.seed(seed)
np.random.seed(seed)

def train_model_structure(train_df: pd.DataFrame) -> BayesianNetwork:
   
    adj_blacklist = set()
    _train_data = train_df.sample(frac=0.1, random_state=seed)
    
    ts = TreeSearch(_train_data, root_node=TARGET_COL)
    m = ts.estimate()
    
    
    G = nx.DiGraph()
    G.add_edges_from(m.edges())
    adj = nx.adjacency_matrix(G).todense()
    if str(adj) not in adj_blacklist:
        adj_blacklist.add(str(adj))
            
        p = m.get_parents(TARGET_COL)
        print(f'Parents of {TARGET_COL}: {p}')
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
    
def estimate_model(model: BayesianNetwork, train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[BayesianNetwork, float]:
    _train_df = train_df.copy()
        
    # Learing CPDs using Maximum Likelihood Estimators
    model = BayesianNetwork(model.edges())
    
    def get_estimator():
        return MaximumLikelihoodEstimator

    model.fit(_train_df, estimator=get_estimator())
    

    X_test = test_df.drop(TARGET_COL, axis='columns')
    ypred = model.predict(X_test)
    test_acc = accuracy_score(test_df[TARGET_COL], ypred[TARGET_COL])
    print(f'Accuracy on test data: {test_acc} for model')
    
    return model, test_acc

def save_model(model: BayesianNetwork, id: int) -> str:
    '''
    Saves models to file and returns list of paths to saved models
    '''

    src_path = os.path.dirname(filedirpath)
    print(src_path)

    paths = []
    
    # Create directories if they don't exist
    os.makedirs(f'{src_path}/bnc_networks/', exist_ok=True)
    os.makedirs(f'{src_path}/bnc_configs/', exist_ok=True)
    os.makedirs(f'{filedirpath}/models/', exist_ok=True)

    # Save model
    NETWriter(model).write_net(f'{filedirpath}/models/credit10k_{id}.net')
    NETWriter(model).write_net(f'{src_path}/bnc_networks/credit10k_{id}.net')

    DATASET_CONFIG = {
        "id": id,
        "name": 'credit10k',
        "filetype": "net",
        "vars": len(train_df.columns),
        "root": TARGET_COL,
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
    model = train_model_structure(train_df)
    plot_model(model)
    trained_model, test_accuracy = estimate_model(model, train_df, test_df)
    print(f'Test accuracy: {test_accuracy}')
    
    save_model(trained_model, 999)
    
    
    
        