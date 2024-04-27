import json
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


from run_experiments_binary import ExperimentRunner
from run import DATASET_CONFIG, run_net_to_odd_compilation, run_encoding, test_if_cnf_satisfiable, read_cnf_from_json, run_plot_odd



def get_table_with_metrics(result_dict, test_accuracy):
    df = pd.DataFrame(result_dict)
    df['test_accuracy'] = test_accuracy
    df['test_accuracy'] = df['test_accuracy'].apply(lambda x: round(x * 100, 2))

    final = df[['ITR_SAT', 'ITR_UNSAT', 'test_accuracy']]
    final['Adherence[%]'] = round(final['ITR_UNSAT'] / (final['ITR_UNSAT'] + final['ITR_SAT']) * 100, 2)
    final['ITR_SAT'] = final['ITR_SAT'].astype(int)
    final['ITR_UNSAT'] = final['ITR_UNSAT'].astype(int)

    final.columns = ['SAT', 'UNSAT', 'Test Acc \%', 'Adherence \%']
    # reorder columns
    final = final[['UNSAT', 'SAT', 'Adherence \%', 'Test Acc \%']]
    # print('ITR results')
    return final

def run_compilation(config_paths):
    successful_compilations = []

    for path in config_paths:

        with open(path, 'r') as f:
            config = json.load(f)

        name = config['name']
        id = config['id']
        config['leaves'] = []
        success = run_net_to_odd_compilation(name, config)
        successful_compilations.append(success)
        print(f'Compilation success: {success}')
        if success:
            odd_filename = f"odd_models/{name}_{id}.odd"
            cnf_filename = f"cnf_files/{name}_{id}.json"
            run_encoding(odd_filename, cnf_filename)

            cnf, _, _, _ = read_cnf_from_json(cnf_filename)
            test_if_cnf_satisfiable(cnf=cnf)

            run_plot_odd(odd_filename=odd_filename, save_path=f'plots/{name}_{id}.png')

        print(f'Finished {name}_{id}')

    print(f'Successful compilations: {successful_compilations}')
    
def run_experiments(model_id: str) -> dict:

    result_dict = {
        'ITR_SAT': [],
        'ITR_UNSAT': [],
        'TOTAL_ITR_TIME': [],
        'TOTAL_FMO_TIME': [],
        'TOTAL_ITR_TIME_PER_QUERY': [],
        'TOTAL_FMO_TIME_PER_QUERY': [],
    }

    for i, path in enumerate([f'/home/ignacy/cmu/bnc-formal-verification/src/bnc_configs/credit10k_{i}.json' for i in [model_id]]):
        with open(path, 'r') as f:
            config = json.load(f)
        
        name = config['name']
        id = config['id']
        
        runner = ExperimentRunner(name, id, logging_level='info')
        runner.run(measure_time=False)
        times = runner.get_times()
        fmo_time = times['fmo'] if times['fmo'] else -1
        itr_time = times['itr'] if times['itr'] else -1
        if fmo_time is not None:
            print(f'Finished {name}_{id} in {fmo_time + itr_time:.0f} ms. Where FMO took {fmo_time:.0f} ms and ITR took {itr_time:.0f} ms.')
        
        ifthen_results_path = os.path.join(runner.artifacts_path, f'ifthen_{name}.json')
        ifthen_results = json.load(open(ifthen_results_path, 'r'))
        itr_unsat_count = 0
        itr_all_count = 0
        for _, result in ifthen_results.items():
            if bool(result['is_UNSAT']):
                itr_unsat_count += 1
            itr_all_count += 1
            
        print(f'ITR_UNSAT: {itr_unsat_count}, ITR_SAT: {itr_all_count - itr_unsat_count}')
        
        
        result_dict['ITR_SAT'].append(itr_all_count - itr_unsat_count)
        result_dict['ITR_UNSAT'].append(itr_unsat_count)
        result_dict['TOTAL_ITR_TIME'].append(itr_time)
        result_dict['TOTAL_FMO_TIME'].append(fmo_time)
        result_dict['TOTAL_ITR_TIME_PER_QUERY'].append(itr_time / itr_all_count)
        result_dict['TOTAL_FMO_TIME_PER_QUERY'].append(fmo_time / itr_all_count)
        
    return result_dict

def transform_mdd_names_back(variable_list: list[str], odd_filepath: str) -> list[str]:
    transformed_list = []
    variables = {}
    
    with open(odd_filepath) as f:
        d = f.readline().replace('[', '').replace(']', '').split(',')
        d[-1] = d[-1][:-1]
        
        variables_order = [x.strip() for x in d]
    
    
    for var in variable_list:
        if var.startswith('Node'):
            name = var.split('_')[1]
            
            if 'TRUE' in name or 'FALSE' in name:
                continue
            
            order_index = variables_order.index(name) + 1 # +1 because variable index in odd starts at 1
            
            s = f'x_{order_index}'
            
            for var2 in variable_list:
                if var2.startswith(s):
                    value = int(var2.split('=')[1].split('th')[0])
                    
                    transformed_list.append(f'{name}={value}th')
                    break
            
            
            
            # for var2 in variable_list:
            #     if var2.startswith(f'x_{index}'):
            #         value = int(var2.split('=')[1].split('th')[0])
                    
            #         transformed_list.append(f'{name}={value}th')
            #         break
    
    return transformed_list
    
def translate_rule_to_set_of_legal_values(rule: list[tuple[str, str, float]],
                                          outcome_name: str,
                                          outcome_value: int,
                                          translation_table: dict[str, dict[str, int]]) -> dict:
    result = {}
    
    rule.append((outcome_name, '==', outcome_value))
    
    for i, (var, op, value) in enumerate(rule):
        value = int(value)
        
        d = translation_table[var]
        allowed = list()
        
        match(op):
            case '>':
                allowed = list(map(lambda x: x[0], filter(lambda item: item[1] > value, d.items())) )
                notallowed = set(d.keys()) - set(allowed)
            case '>=':
                allowed = list(map(lambda x: x[0], filter(lambda item: item[1] >= value, d.items())) )
                notallowed = set(d.keys()) - set(allowed)
            case '<':
                allowed = list(map(lambda x: x[0], filter(lambda item: item[1] < value, d.items())) )
                notallowed = set(d.keys()) - set(allowed)
            case '<=':
                allowed = list(map(lambda x: x[0], filter(lambda item: item[1] <= value, d.items())) )
                notallowed = set(d.keys()) - set(allowed)
            case '==':
                allowed = list(map(lambda x: x[0], filter(lambda item: item[1] == value, d.items())) )
                notallowed = set(d.keys()) - set(allowed)
            case _:
                raise ValueError(f'Operator {op} not recognized')
    
        if var not in result:
            result[var] = {}
            result[var]['allowed'] = allowed
            result[var]['notallowed'] = list(notallowed)
        else:
            result[var]['allowed'] = list(set(result[var]['allowed']).intersection(set(allowed)))
            result[var]['notallowed'] = list(set(result[var]['notallowed']).union(set(notallowed)))
        
    return result

def plot_legal_values(legal_values: dict[str, dict[str, list[str]]],
                      translation_table: dict[str, dict[str, int]],
                      target_col: str,
                      dataset_name: str,
                      model_id: int,
                      artifacts_path: str,
                      coverage: int | None = None,
                      n: int | None = None,
                      save_name: str | None = None
                      ) -> None:

    
    fig, axs = plt.subplots(3, 4, figsize=(16, 6))
    
 
    # Plot also all variables in translation table that are not in legal_values
    for col in translation_table.keys():
        if col not in legal_values.keys():
            legal_values[col] = {}
            legal_values[col]['allowed'] = list(translation_table[col].keys())
            legal_values[col]['notallowed'] = []
            
    
    axs = axs.flatten()
    columns = sorted(legal_values.keys())
    # move target column to the end
    columns.remove(target_col)
    columns.append(target_col)
    
    red = "#A6192E"
    green = "#789F90"
    white = "#FFFFFF"
    
    
    
    for i, col in enumerate(columns):
        labels = translation_table[col].keys()
        ticks = translation_table[col].values()
        colors = [green if x in legal_values[col]['allowed'] else red for x in labels]

        # Transpose the plot
        axs[i].barh(np.array(list(ticks)), np.ones(len(ticks)), color=colors)

        # hide ticks on x axis
        axs[i].xaxis.set_ticks([])

        # Set the ticks on y axis
        axs[i].set_yticks(np.array(list(ticks)))
        # axs[i].set_yticks([])

        # Set the labels on y axis
        # axs[i].set_yticklabels(labels)
        
        
        # Add labels on bars
        
        rects = axs[i].patches
        for rect, label in zip(rects, labels):
            if label in legal_values[col]['allowed']:
                color = 'white'
            else:
                color = 'white'
            axs[i].text(rect.get_width() - 0.95, rect.get_y() + rect.get_height() / 2,
                        label, ha='left', va='center', color=color, fontsize=12)
        

        # Remove the frame
        axs[i].set_frame_on(False)
        
        # # Add separation lines between plots
        # axs[i].axvline(x=1.5, color='black', linewidth=0.5, linestyle='--', ymax=1, ymin=0.2)
        
        # # Add horizontal line as separation
        # axs[i].axhline(y=-1, color='black', linewidth=0.5, linestyle='--', xmax=1, xmin=0)
        
        # Add axis title
        axs[i].set_title(col, fontsize=15)
        
    title = f'Legal values for each variable'
    if coverage:
        title += f'. Instances covered: {coverage}' 
        
        if n:
            title += f' out of {n}, ({coverage/n*100:.4f}%)'
        
    # Add supertitle
    # fig.suptitle(title, fontsize=10)
    
    save_name = save_name if save_name else f'legal_values_{dataset_name}_{model_id}'
    
    
    
    plt.savefig(os.path.join(artifacts_path, f'{save_name}.png'), dpi=300)
    plt.savefig(os.path.join(artifacts_path, f'{save_name}.eps'), dpi=300)
    

    plt.tight_layout()
    plt.show()
    
def filter_out_region_of_a_rule(rule: dict, data: pd.DataFrame, target_col: str) -> pd.DataFrame:
    mask = np.ones(len(data), dtype=bool)
    
    for colname in data.columns:
        if colname == target_col:
            continue
        
        if colname in rule.keys():
            mask = mask & data[colname].isin(rule[colname]['allowed'])
            
            
    return data[mask]

def analyse_records(
                    rules_df: pd.DataFrame,
                    data: pd.DataFrame,
                    translation_table: dict[str, dict[str, int]],
                    target_col: str,
                    dataset_name: str,
                    model_id: int,
                    artifacts_path: str,
                    plot: bool = True, 
                    print_rules: bool = False, 
                    show_covered_instances: bool = False,
                    unsat: bool = True, 
                    how_many: int = 5,
                    ) -> None:

    rows = rules_df[rules_df['ifthen_UNSAT'] == unsat]
    
    # sort by coverage 
    rows = rows.sort_values(by='coverage', ascending=False)
    
    
    for i, (_, row) in enumerate(rows.iterrows()):
        
        if i == how_many:
            break
        
        legal_values = translate_rule_to_set_of_legal_values(row['rule'], 
                                                            target_col,
                                                            row['class'], 
                                                            translation_table)
        
        covered_instances = filter_out_region_of_a_rule(legal_values, data, target_col)
        
        if show_covered_instances:
            print(f'Covered instances: {len(covered_instances)}')

        if print_rules:
            # Print the legal values for each variable
            for var in legal_values.keys():
                print(f'Variable: {var}')
                print(f'Allowed values: {legal_values[var]["allowed"]}')
                print(f'Not allowed values: {legal_values[var]["notallowed"]}')
                print()
            
        if plot:
            plot_legal_values(legal_values, translation_table=translation_table,   target_col=target_col, dataset_name=dataset_name, model_id=model_id, artifacts_path=artifacts_path,
                              coverage=len(covered_instances), n=len(data), save_name=f'legal_values_{dataset_name}_{model_id}_{i}') 

def print_rule(rule_dict: dict) -> None:

    print(f'Rule: {rule_dict["rule"]}')
    print(f'Outcome: {rule_dict["class"]}')
    print(f'Ifthen Verification result: {rule_dict["ifthen_UNSAT"]}')


    print(f'True variables - names: {rule_dict["ifthen_True_Vars"]}')
    print(f'False variables - names: {rule_dict["ifthen_False_Vars"]}')
