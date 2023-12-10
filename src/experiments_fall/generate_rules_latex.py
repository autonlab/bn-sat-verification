import pandas as pd
import json
import os 
import numpy as np

print(os.getcwd())

from experiment_utils import credit10k_translation_table


def translate_range(_s, _v, feature):
    
    r = np.zeros(len(credit10k_translation_table[feature]))
    match _s:
        case '<=':
            r[:_v+1] = 1
        case '<':
            r[:_v] = 1
        case '>=':
            r[_v:] = 1
        case '>':
            r[_v+1:] = 1
        case '=':
            r[_v] = 1
        case _:
            raise ValueError(f'Unknown sign {_s}')
        
    return r
        
        
        

rules = [x['rule'] for x in json.load(open('src/experiments_fall/expert_rules_dedup.json', 'r'))]
classes = [x['class'] for x in json.load(open('src/experiments_fall/expert_rules_dedup.json', 'r'))]
print(classes)

fixed_rules = []
for rule in rules:
    new_rule = []
    for feature, sign, value in rule:
        value = int(value)
        if (sign == '<=' or sign == '<') and value == 0:
            new_rule.append((feature, '=', value))
        elif (sign == '>' or sign == '>=') and value == len(credit10k_translation_table[feature]) - 1:
            new_rule.append((feature, '=', value))
        elif sign == '==':
            new_rule.append((feature, '=', value))
        else:
            new_rule.append((feature, sign, value))
            
    fixed_rules.append(new_rule)
    
    
columns = credit10k_translation_table.keys()
index = [f'rule_{i}' for i in range(len(fixed_rules))]
        
df = pd.DataFrame(columns=columns, index=index)
df = df.fillna('-')

for i, rule in enumerate(fixed_rules):
    for feature, sign, value in rule:
        if df.loc[f'rule_{i}', feature] != '-':
            df.loc[f'rule_{i}', feature] += sign + ' ' + str(value)
            
            # _s, _v = df.loc[f'rule_{i}', feature].split(' ')
            # _v = int(_v)
            
            # r = translate_range(_s, _v, feature)
            # r2 = translate_range(sign, value, feature)
            
            # r = r.astype(bool) & r2.astype(bool)
            # print(r)
            
            # if r.sum() == 0:
            #     raise ValueError('Empty intersection')
            # elif r.sum() == 1:
            #     _v = np.where(r == 1)[0][0]
            #     df.loc[f'rule_{i}', feature] =  '= ' + str(_v)
            # else:
            #     start = np.where(r == 1)[0][0]
            #     end = np.where(r == 1)[0][-1]
                
            #     df.loc[f'rule_{i}', feature] = f'< {end}' if end == start + 1 else f'< {end+1}'
                
        
        else:
            df.loc[f'rule_{i}', feature] = sign + ' ' + str(value)
        

print(df.T)

# to latex
latex = df.T.to_latex(escape=False, column_format='l|cccccccccccc')

latex = latex.replace('\\toprule', '\\hline')
latex = latex.replace('\\midrule', '\\hline')
latex = latex.replace('\\bottomrule', '\\hline')

latex = latex.replace('rule_', 'rule')

# add $ signs in each cell
latex = latex.replace('=', '$=$')
latex = latex.replace('<', '$<$')
latex = latex.replace('>', '$>$')
latex = latex.replace('>=', '$\\geq$')
latex = latex.replace('<=', '$\\leq$')


print(latex)