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

T = 70
N = 10


def train_model_structures(train_df: pd.DataFrame, T: int) -> list:
    models = []
    adj_blacklist = set()
    
    for i in range(T):
        _train_data = train_df.sample(frac=0.1, random_state=seed + i)
        
        if random.random() < 0/5:
            hc = HillClimbSearch(_train_data)
            scoring = random.choice(['k2score', 'bicscore'])
            espilon = random.choice([0.0001, 0.0005, 0.001])
            m = hc.estimate(scoring_method=scoring, epsilon=espilon)
            
        elif random.random() < 0/5:
            pc = PC(_train_data)
            variant = random.choice(['orig', 'stable', 'parallel'])
            ci_test = random.choice(['pearsonr', 'g_sq', 'chi_square'])
            m = pc.estimate(max_cond_vars=len(_train_data.columns) - 2, variant=variant, ci_test=ci_test)
        else:    
            if random.random() < 0.5:
                ts = TreeSearch(_train_data, root_node=TARGET_COL)
                m = ts.estimate()
            else:
                ts = TreeSearch(_train_data)
                m = ts.estimate(estimator_type='tan', class_node=TARGET_COL)
                
        G = nx.DiGraph()
        G.add_edges_from(m.edges())
        adj = nx.adjacency_matrix(G).todense()
        if str(adj) not in adj_blacklist:
            adj_blacklist.add(str(adj))
                
            p = m.get_parents(TARGET_COL)
            print(f'Parents of {TARGET_COL}: {p}')
            if len(p) == 0: # no parents
                models.append(m)

    print(f'All models done')

    return models


def plot_models(models: list) -> None:
    fig, ax = plt.subplots(len(models) // 3 + 1, 3, figsize=(15, 10))
    ax = ax.ravel()
    for i, model in enumerate(models):
            G = nx.DiGraph()
            G.add_edges_from(model.edges())
            pos = nx.spring_layout(G)
            nx.draw(G, 
                    pos, 
                    with_labels=True,
                    node_size=200,
                    node_color="skyblue",
                    ax=ax[i]
                    )
    plt.tight_layout()
    plt.show()
    
def estimate_models(models: list, train_df: pd.DataFrame, N: int, test_df: pd.DataFrame) -> tuple[list[BayesianNetwork], list[float]]:
    trained_models = []
    test_accuracies = []
    
    

    it = 0
    # fold_len = len(train_df) // N
    
    while len(trained_models) < N:
        # _train_df = train_df[it*fold_len:(it+1)*fold_len]
        _train_df = train_df.copy()
            
        if it > len(models):
            i = random.randint(0, len(models) - 1)
        else:
            i = it
        
        # Learing CPDs using Maximum Likelihood Estimators
        model = BayesianNetwork(models[i].edges())
        
        def get_estimator():
            if random.random() < 1/3:
                return MaximumLikelihoodEstimator
            else:
                return BayesianEstimator
            # else:
            #     return ExpectationMaximization

        model.fit(_train_df, estimator=get_estimator())
        trained_models.append(model)

        X_test = test_df.drop(TARGET_COL, axis='columns')
        ypred = model.predict(X_test)
        test_acc = accuracy_score(test_df[TARGET_COL], ypred[TARGET_COL])
        test_accuracies.append(test_acc)
        print(f'Accuracy on test data: {test_acc} for model {i}')
        
        it+=1 
        
    return trained_models, test_accuracies

def save_models(models: list, accuracies: list) -> list:
    '''
    Saves models to file and returns list of paths to saved models
    '''

    src_path = os.path.dirname(filedirpath)
    print(src_path)

    paths = []

    for i, model in enumerate(models):
        NETWriter(model).write_net(f'{filedirpath}/models/credit10k_{i}.net')
        NETWriter(model).write_net(f'{src_path}/bnc_networks/credit10k_{i}.net')
        
        index = [f'credit10k_{i}' for i in range(len(models))]
        acc_df = pd.DataFrame({'index': index, 'accuracy': accuracies})
        acc_df.to_csv('models/credit10k_accuracies.csv', index=True)

        DATASET_CONFIG = {
            "id": i,
            "name": 'credit10k',
            "filetype": "net",
            "vars": len(train_df.columns),
            "root": TARGET_COL,
            "leaves": 6,
            "threshold": 0.5,
            "input_filepath": "../bnc_networks/",
            "output_filepath": "../odd_models/"
        }

        s = f'{src_path}/bnc_configs/credit10k_{i}.json'
        paths.append(s)
        with open(s, 'w') as f:
            json.dump(DATASET_CONFIG, f, indent=4)
            
    return paths


if __name__ == '__main__':
    models = train_model_structures(train_df, T)
    plot_models(models)
    trained_models, test_accuracies = estimate_models(models, train_df, N, test_df)
    print(f'Average test accuracy: {np.mean(test_accuracies)}')
    print(f'All test accuracies: {test_accuracies}')
    
    save_models(trained_models, test_accuracies)
    
    
        