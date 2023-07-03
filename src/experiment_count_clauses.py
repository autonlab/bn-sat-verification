import os 
import json 
import pandas

cnf_dirpath = os.path.join(os.getcwd(), 'cnf_files')
model_dirpath = os.path.join(os.getcwd(), 'bnc_networks')
all_models = os.listdir(model_dirpath)
all_files = os.listdir(cnf_dirpath)

save_path = os.path.join(os.getcwd(), 'results', 'mdd_stats.csv')
latex_save_path = os.path.join(os.getcwd(), 'results', 'mdd_stats.tex')
if os.path.exists(save_path):
    os.remove(save_path)
if not os.path.exists(os.path.join(os.getcwd(), 'results')):
    os.mkdir(os.path.join(os.getcwd(), 'results'))

literals = []
nets = []
clauses = [] 
nodes = []
edges = []
variable_values = []

for filename in all_files:
    
    cnf_path = os.path.join(cnf_dirpath, filename)
    
    if '.json' not in filename:
        continue

    _json = json.load(open(cnf_path, 'r'))

    inverse_mapping = _json['map_inv']
    mapping = _json['map']
    encoding = _json['cnf']

    literals_count = max(inverse_mapping.keys(), key=lambda x: int(x))
    clauses_count = len(encoding)
    count_nodes = len([x for x in mapping.keys() if x.startswith('Node')])
    print(count_nodes)
    count_edges = len([x for x in mapping.keys() if x.startswith('edge')])
    variable_values_count = [x for x in mapping.keys() if x.startswith('x')]
    
    literals.append(literals_count)
    nets.append(filename[:-5])
    clauses.append(clauses_count)
    nodes.append(count_nodes)
    edges.append(count_edges)
    variable_values.append(len(variable_values_count))
    

models_stats = {}

for filename in all_models:
    if not filename.endswith('.net'):
        continue
    
    with open(os.path.join(model_dirpath, filename), 'r') as f:
        # Go through the file and count the number of nodes
        # and edges
        count_nodes = 0
        count_edges = 0

        for line in f.readlines():
            if line.startswith('node'):
                count_nodes += 1
        
        
        models_stats[filename[:-4]] = {'nodes': count_nodes, 'edges': count_edges}
    
    

df = pandas.DataFrame({ 'net': nets, 
                        'bnc_nodes': [models_stats[x]['nodes'] if x in models_stats else None for x in nets],
                        'cnf_literals': literals,
                        'cnf_clauses': clauses,
                        'mdd_nodes': nodes,
                        'mdd_edges': edges,
                        'mdd_variable_values': variable_values,
                       })
df.to_csv(save_path, index=False)

# Pandas to latex
latex_df = df.to_latex(index=False)
with open(latex_save_path, 'w') as f:
    f.write(latex_df)

print(df)