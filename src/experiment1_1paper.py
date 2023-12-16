import json
import os
import pandas as pd

if 'src' not in os.getcwd():
    os.chdir('src')
    
print(os.getcwd())

cnf_path = 'cnf_files/'
file_paths = [
    'admission_1.json',
    'asia_1.json',
    'child_1.json',
    'alarm_1.json',
    'win95pts_1.json',
]

df = pd.DataFrame(columns=['literals', 'clauses'])

for file_path in file_paths:
    with open(cnf_path + file_path, 'r') as f:
        cnf = json.load(f)
        
        clauses_cnt = len(cnf['cnf'])
        literals_cnt = len(cnf['map_inv'])

        print(f'{file_path} & {clauses_cnt} & {literals_cnt} \\\\')
        
        # use file name as index
        df.loc[file_path] = [literals_cnt, clauses_cnt]
        
        
print(df.T.to_latex(index=True, escape=False))
        