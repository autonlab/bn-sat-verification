# Encode OMDD (Ordered Multivalue Decision Diagram) to a CNF (Conjunctive Normal Form) formula
# Using the Tseitin encoding method
# Based on paper: "On CNF Encodings of Decision Diagrams"
import json
import os
import logging
from collections import defaultdict

from node import Node
from odd_parser import read_obdd_from_file, draw_obdd
from typing import Dict, List, Tuple
from pysat.formula import CNF
from pysat_solver import pysat_solver

def exactly_one(literals: List[int]) -> List[List[int]]:
    '''
    Encodes that exactly one of the literals is true
    '''
    
    def at_least_one(literals: List[int]) -> List[int]:
        '''
        Encodes that at least one of the literals is true.
        So it is OR of all variables.
        '''
        return literals
    
    def at_most_one(literals: List[int]) -> List[List[int]]:
        '''
        Encodes that at most one of the literals is true
        This 
        '''
        clauses = []
        for i in range(len(literals)-1):
            for j in range(i+1, len(literals)):
                clauses.append([-literals[i], -literals[j]])
                
        return clauses

    return [at_least_one(literals)] + at_most_one(literals)


def add_node_clauses(odd: Dict[int, Node]) -> Tuple[CNF, Dict, Dict]:
    '''
    Here we add the clauses that encode the nodes using Tseitin transformation.
    
    The Tseitin encoding introduce Boolean variables representing the formula of each edge. 
    Let v be a node at level i, with outgoing edges j_0, ..., j_n
    Let u be the node at level i+1 to which the edge j_k of v leads to.
    Then we add following clauses:
    T1: v -> V_j epsilon_j
    T2: epsilon -> v
    T3: epsilon -> u
    T4: epsilon -> x_i = j
    T5: u and x_i = j -> epsilon
    '''
    var_idx = 1
    mapping = {}
    mapping_inv = {}
    
    cnf = CNF()
    incoming_edges_map = defaultdict(list) # Map from node index to list of incoming edges
    variable_values_edges_map = defaultdict(list) # Map from x_i = j to list of edges that have this value
    
    def add_to_mapping(element):
        if element not in mapping:    
            nonlocal var_idx
            mapping[element] = var_idx
            mapping_inv[var_idx] = element
            var_idx += 1
    
    for i in sorted(odd.keys()): # For all nodes in the ODD
        v_i  = odd[i] # Node at level i
        add_to_mapping(v_i)
        
        all_outgoing_edges = list() # Store all outgoing edges of the node v_i
        
        terminal_node = False
        if odd[i].variable_name == "TRUE":
            # True leaf node, add clause that it is true
            cnf.append([mapping[v_i]])
            terminal_node = True
        if odd[i].variable_name == "FALSE":
            # False leaf node, add clause that it is false
            cnf.append([-mapping[v_i]])
            terminal_node = True
        
        if not terminal_node:
            for j, v_child_index in enumerate(v_i.edges): # For all edges of the node v_i
                v_child = odd[v_child_index] # Node at level i+1, to which the edge j of v_i leads to
                add_to_mapping(v_child) # Add to mapping (if not already there)
                
                all_outgoing_edges.append(v_child) # Add to list of outgoing edges for T1 purpose
                
                epsilon = f'edge_{v_i.index}_{v_child.index}' # Name of the edge variable
                add_to_mapping(epsilon) # Add to mapping (if not already there)
                incoming_edges_map[v_child.index].append(epsilon) # Add to incoming edges map
                
                x_i = f'x_{v_i.variable_index} = {j}th value' # Name of the variable that represents the value of the node v_i = j
                add_to_mapping(x_i) # Add to mapping (if not already there)
                
                variable_values_edges_map[x_i].append(epsilon) # Add to variable values edges map
                
                # Following clauses are added to the cnf formula (Tseitin encoding) 
                
                # T2: epsilon -> v_i
                cnf.append([-mapping[epsilon], mapping[v_i]]) 

                # T3: epsilon -> v_child
                cnf.append([-mapping[epsilon], mapping[v_child]])
                
                # T4: epsilon -> x_i = j
                cnf.append([-mapping[epsilon], mapping[x_i]])
                
                # T5: v_child and x_i = j -> epsilon
                # TODO: Make sure that this is correct
                # For now I added to the left side that parent node is also true
                # Otherwise levels that have more than one node will not work!!!
                cnf.append([-mapping[v_child], -mapping[x_i], -mapping[v_i], mapping[epsilon]])
                
                # P1: v_i and x_ji -> epsilon
                cnf.append([-mapping[v_i], -mapping[x_i], mapping[epsilon]])
                
            # T1: v_i -> V_j epsilon_j
            cnf.append([-mapping[v_i]] + [mapping[epsilon] for epsilon in all_outgoing_edges])
            
        # P2: v_i -> exists epsilon_(i-1)_i \ where i != 1 (i.e. not root node)
        if i != 1:
            #logging.debug('INCOMING EDGES:', incoming_edges_map[v_i.index])
            cnf.append([-mapping[v_i]] + [mapping[inc_edge] for inc_edge in incoming_edges_map[v_i.index]])
    
    # P3: x_ij -> epsilon_i_j
    for x, epsilons in variable_values_edges_map.items():
        cnf.append([-mapping[x]] + [mapping[epsilon] for epsilon in epsilons])
        
    # P4: ExactlyOne(v for v in odd_nodes_on_level_i)
    levels = defaultdict(list)
    for i in sorted(odd.keys()):
        levels[odd[i].variable_index].append(odd[i])
        
    for level in levels.values():
        literals = [mapping[v] for v in level]
        exactly_one_encoding = exactly_one(literals)
        for clause in exactly_one_encoding:
            cnf.append(clause)
    
    return cnf, mapping, mapping_inv
    
def print_with_names(cnf: CNF, mapping_inv: Dict) -> None:
    '''
    Print the cnf formula with the names of the variables
    '''
    for clause in cnf.clauses:
        logging.debug([mapping_inv[abs(lit)] if lit > 0 else f'-{mapping_inv[abs(lit)]}' for lit in clause])

def print_mapping(mapping: Dict) -> None:
    '''
    Print the mapping in a nice way
    '''
    for key, value in mapping.items():
        logging.debug(f'{key:{" "}{"<"}{3}}: {value}')
        
def save_cnf_to_json(cnf: CNF, mapping_inv: Dict, mapping: Dict, path: str) -> None:
    '''
    Save the cnf formula and the mapping to a json file
    '''
    path = os.path.join(os.path.dirname(__file__), path)
    
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
        
    mapping_inv = {str(key): str(value) for key, value in mapping_inv.items()}
    mapping = {str(key): str(value) for key, value in mapping.items()}
    
    with open(path, 'w') as f:
        json.dump({
            'cnf': cnf.clauses,
            'mapping_inv': mapping_inv,
            'mapping': mapping
        }, f, indent=4)
        
def read_cnf_from_json(path: str) -> Tuple[CNF, Dict, Dict]:
    '''
    Read the cnf formula and the mapping from a json file
    
    Returns:
        cnf: pysat CNF object
        mapping_inv: mapping from variable index to variable name
        mapping: mapping from variable name to variable index (in CNF)
    '''
    path = os.path.join(os.path.dirname(__file__), path)
    
    with open(path, 'r') as f:
        data = json.load(f)
        
    cnf = CNF()
    cnf.clauses = data['cnf']
    
    return cnf, data['mapping_inv'], data['mapping']

if __name__ == '__main__':
    # -------------------------------
    # This is the example that encodes following OBDD
    #                        0 --> False
    #   0 --> WorkExperience 1 --> True 
    # GPA
    #   1 --> WorkExperience 1 --> True
    #                        0 --> False
    # -------------------------------
    
    # gpa = Node(0, 0, 1, 2, "GPA")
    # we_1 = Node(1, 1, 3, 4, "WE_1")
    # we_2 = Node(2, 2, 3, 4, "WE_2")
    # ter_t = Node(3, 3, None, None, "TRUE")
    # ter_f = Node(4, 4, None, None, "FALSE")
    
    # odd = {
    #     0: gpa,
    #     1: we_1,
    #     2: we_2,
    #     3: ter_t,
    #     4: ter_f
    # }
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert ODD to CNF')
    
    parser.add_argument('--odd', type=str, help='Path to the ODD file')
    parser.add_argument('--cnf', type=str, help='Path to the CNF file')
    parser.add_argument('--verbose', action='store_true', help='Print debug messages')
    
    odd_path = parser.parse_args().odd
    cnf_path = parser.parse_args().cnf
    verbose = parser.parse_args().verbose
    
    # Set logging level
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    if '.odd' not in odd_path:
        odd_path += '.odd'
    if '.json' not in cnf_path:
        cnf_path += '.json'
    
    odd = read_obdd_from_file(f'{odd_path}')
    
    _cnf, _map, _map_inv = add_node_clauses(odd)
    
    save_cnf_to_json(_cnf, _map_inv, _map, f'{cnf_path}')
 
    logging.debug(_cnf.clauses)
    
    print_mapping(_map_inv)
    
    print_with_names(_cnf, _map_inv)
    
    should_SAT = PySATSolver().solve(_cnf, assumptions=[])
    assert should_SAT, "Should be SAT"
    
    should_UNSSAT = PySATSolver().solve(_cnf, assumptions=[1, 13])
    assert not should_UNSSAT, "Should be UNSAT"