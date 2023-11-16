import numpy as np
from math import floor
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pandas as pd 
import json 
from experiment_utils import prep_data, discretize_data
import logging
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree


def extract_rules(tree: DecisionTreeClassifier,
                  feature_names: list,
                  node_index: int = 0,
                  rule: list = None,
                  floor_threshold: bool = True,
                  only_pure_leaves: bool = True,
                  feature_ranges: dict = None,
                  ) -> list:
    ''' 
    Extract rules from a scikit-learn DecisionTreeClassifier.
    '''
    if node_index == -1:
        return []

    if rule is None:
        rule = list()

    # Get the feature index and threshold for the current node
    feature_index = tree.feature[node_index]
    threshold = tree.threshold[node_index]
    # Extract feature name and create rule
    feature_name = feature_names[feature_index]
        
    if feature_ranges:
        # clip threshold to feature range
        threshold = max(threshold, feature_ranges[feature_name][0])
        threshold = min(threshold, feature_ranges[feature_name][1])
        
    if floor_threshold:
        threshold = floor(threshold)
        
    threshold = float(threshold)
    

    if tree.children_left[node_index] == tree.children_right[node_index]:
        # Leaf node, check for purity
        class_label = np.argmax(tree.value[node_index])
        classes = np.unique(tree.value[node_index])
        if classes.shape[0] == 2 and 0 in classes or not only_pure_leaves:
            # Leaf node is pure
            rule_with_class = {'rule':  rule, 'class': int(class_label)}
            return [rule_with_class]
        else:
            return []
        
    
    if rule:
        new_rule_left = rule + [(feature_name, "<=" , threshold)]
        new_rule_right = rule + [(feature_name, ">" , threshold)]
    else:
        new_rule_left = [(feature_name, "<=", threshold)]
        new_rule_right = [(feature_name, ">" , threshold)]

    # Recursively traverse left and right branches
    left_rules = extract_rules(tree, feature_names, tree.children_left[node_index], new_rule_left, floor_threshold, only_pure_leaves, feature_ranges)
    right_rules = extract_rules(tree, feature_names, tree.children_right[node_index], new_rule_right, floor_threshold, only_pure_leaves, feature_ranges)
    return left_rules + right_rules

def add_coverage_to_rules(rules: list, X: pd.DataFrame) -> list:
    for rule in rules:
        for i, (feature, op, threshold) in enumerate(rule['rule']):
            if i == 0:
                mask = X[feature] <= threshold if op == '<=' else X[feature] > threshold
            else:
                mask = mask & (X[feature] <= threshold if op == '<=' else X[feature] > threshold)
                
        rule['coverage'] = round(mask.sum() / X.shape[0], 3)
    
    return rules

def save_rules_to_json(rules: list, filename: str = 'rules') -> str:  
    path = f'{filename}.json'
    with open(f'{filename}.json', 'w') as f:
        json.dump(rules, f, indent=4)
        
    return path 

def pretty_print(rules: list, X: pd.DataFrame, y: pd.Series | pd.DataFrame | np.ndarray) -> None:
    '''
    Pretty print rules.
    '''
    
    for rule in rules:
        print('------'*10)
        
        for i, (feature, op, threshold) in enumerate(rule['rule']):
            if i == 0:
                mask = X[feature] <= threshold if op == '<=' else X[feature] > threshold
            else:
                mask = mask & (X[feature] <= threshold if op == '<=' else X[feature] > threshold)
                
        X_rule = X[mask]
        y_rule = y[mask]
        
        print(f'Rule: {rule["rule"]}')
        print(f'Rule class: {rule["class"]}')
        
        print(f'{y_rule.value_counts()}')
        print(f'Coverage: {rule["coverage"]}')
    
    print('------'*10)
    print(f'Overall number of rules: {len(rules)}')
        
def display_tree(tree: DecisionTreeClassifier, feature_names: list) -> None:
    fig, ax = plt.subplots(figsize=(15, 6))
    plot_tree(tree, feature_names=feature_names, ax=ax)
    plt.tight_layout()
    plt.show()        
    
def train_and_extract_rules(X: pd.DataFrame, 
                            y: pd.Series | pd.DataFrame | np.ndarray, 
                            feature_names: list, 
                            floor_threshold: bool = True, 
                            only_pure_leaves: bool = True, 
                            feature_ranges: dict = None,
                            random_state: int = 32,
                            criterion: str = 'entropy',
                            splitter: str = 'best',
                            display_trees: bool = False,
                            ) -> list:
    '''
    Train a DecisionTreeClassifier and extract rules.
    '''
    tree = DecisionTreeClassifier(random_state=random_state, criterion=criterion, splitter=splitter)
    tree.fit(X, y)
    
    if display_trees:
        display_tree(tree, feature_names)
    
    logging.info(f'Training accuracy: {accuracy_score(y, tree.predict(X)):.3f}')
    
    rules = extract_rules(tree.tree_, feature_names, floor_threshold=floor_threshold, only_pure_leaves=only_pure_leaves, feature_ranges=feature_ranges)
    rules = add_coverage_to_rules(rules, X)
    
    logging.info(f'Extracted {len(rules)} rules.')
    
    return rules

def deduplicate_list_of_rules(list_of_rules: list) -> list:
    '''
    Deduplicate a list of rules.
    '''
    list_of_rules = [json.dumps(rule, sort_keys=True) for rule in list_of_rules]
    list_of_rules = list(set(list_of_rules))
    list_of_rules = [json.loads(rule) for rule in list_of_rules]
    
    return list_of_rules

def filter_rules(rules: list, min_cov: float = 0.001) -> list:
    '''
    Filter rules by coverage.
    '''
    return [rule for rule in rules if rule['coverage'] >= min_cov]

def check_overlap_and_collapse(rules: list) -> list:
    '''
    Check a rule has two if statements on feature and collapse them.
    '''
    new_rules = []
    for rule in rules:
        d  = {}  
        constraints = rule['rule']
        for feature, sign, value in constraints:
            value = float(value)
            if not feature in d:
                d[feature] = (-np.inf, np.inf)
           
            _min, _max = d[feature]
            if sign == '<=':
                d[feature] = (_min, min(_max, value))
            if sign == '>':
                d[feature] = (max(_min, value), _max)   
                    
        new_rule = []
        for feature, (min_, max_) in d.items():
            if min_ == -np.inf:
                new_rule.append((feature, '<=', max_))
            elif max_ == np.inf:
                new_rule.append((feature, '>', min_))
            else:
                new_rule.append((feature, '<=', max_))
                new_rule.append((feature, '>', min_))
                
        new_rules.append({'rule': new_rule, 'class': rule['class'], 'coverage': rule['coverage']})
    return new_rules            


if __name__ == '__main__':
    from experiment_utils import credit_pipeline
    import os 
    
    filedir = os.path.dirname(os.path.realpath(__file__))
    
    NAME = 'credit10k'
    DATA_PATH = os.path.join(filedir, 'data', f'{NAME}.csv') 
    TRIALS = 5
    RANDOM_START_SEED = 32
    np.random.seed(RANDOM_START_SEED)
    
    logging.basicConfig(level=logging.INFO)
    
    raw_data = pd.read_csv(DATA_PATH)
    train_df, test_df, CLASS_FEATURE_NAME = credit_pipeline(raw_data)
    
    data = pd.concat([train_df, test_df])
    
    X = data.drop(columns=[CLASS_FEATURE_NAME])
    y = data[CLASS_FEATURE_NAME]
    
    feature_names = X.columns
    feature_ranges = {feature: (X[feature].min(), X[feature].max()) for feature in feature_names} 
    
    
    
    list_of_rules = []
    for i in tqdm(range(TRIALS), desc='Extracting rules'):  
        splitter = np.random.permutation(['best', 'random'])[0]
        criterion = np.random.permutation(['entropy', 'gini', 'log_loss'])[0]
        rules = train_and_extract_rules(X, y, feature_names, feature_ranges=feature_ranges, random_state=RANDOM_START_SEED + i, criterion=criterion, splitter=splitter)
        list_of_rules += rules
    
    list_of_rules = add_coverage_to_rules(list_of_rules, X)
    
    list_of_rules = deduplicate_list_of_rules(list_of_rules)
    
    list_of_rules = filter_rules(list_of_rules, min_cov=0.002)
    
    list_of_rules = check_overlap_and_collapse(list_of_rules)
    
    pretty_print(list_of_rules, X, y)
    
    save_rules_to_json(list_of_rules, f'{filedir}/rules_{NAME}')
    

