# Encode OMDD (Ordered Multivalue Decision Diagram) to a CNF (Conjunctive Normal Form) formula
# Using the Tseitin encoding method
# Based on paper: "On CNF Encodings of Decision Diagrams"
import json
import os
import logging
from collections import defaultdict

from utils.node import Node
from odd_parser import read_obdd_from_file, draw_obdd
from typing import Dict, List, Tuple
from pysat.formula import CNF
from verifications.pysat_solver import PySATSolver
from utils.cnf_json_parser import *
from encoder import Encoder

class TseitinEncoder(Encoder):
    
    def __init__(self) -> None:
        super().__init__()
 
    def encode_to_cnf(self, odd: Dict[int, Node]) -> Tuple[CNF, Dict, Dict]:
        '''
        Here we add the clauses that encode the nodes using Tseitin transformation.
        
        The Tseitin encoding introduce Boolean variables representing the formula of each edge. 
        Let v be a node at level i, with outgoing edges j_0, ..., j_n
        Let u be the node at level i+1 to which the edge j_k of v leads to.
        Then we add following clauses:
        
        Tseitin
            T1: v -> V_j epsilon_j
            T2: epsilon -> v
            T3: epsilon -> u
            T4: epsilon -> x_i = j
            T5: u and x_i = j -> epsilon
        Path-based
            P1, P2, P3, P4
        '''
        var_idx = 1
        incoming_edges_map = defaultdict(list) # Map from node index to list of incoming edges
        variable_values_edges_map = defaultdict(list) # Map from x_i = j to list of edges that have this value
        
        def add_to_mapping(element):
            if element not in self.mapping:    
                nonlocal var_idx
                self.mapping[element] = var_idx
                self.mapping_inv[var_idx] = element
                var_idx += 1
        
        for i in sorted(odd.keys()): # For all nodes in the ODD
            v_i  = odd[i] # Node at level i
            add_to_mapping(v_i)
            
            all_outgoing_edges = list() # Store all outgoing edges of the node v_i
            
            terminal_node = False
            if odd[i].variable_name == "TRUE":
                # True leaf node, add clause that it is true
                self.cnf.append([self.mapping[v_i]])
                terminal_node = True
            if odd[i].variable_name == "FALSE":
                # False leaf node, add clause that it is false
                self.cnf.append([-self.mapping[v_i]])
                terminal_node = True
            # if i == 1:
            #     # Root node, add clause that it is true
            #     self.cnf.append([self.mapping[v_i]])
            
            if not terminal_node:
                for j, v_child_index in enumerate(v_i.edges): # For all edges of the node v_i
                    
                    v_child = odd[v_child_index] # Node at level i+1, to which the edge j of v_i leads to
                    add_to_mapping(v_child) # Add to mapping (if not already there)
                    
                    
                    epsilon = f'edge_{v_i.index}_{v_child.index}_({i}_{j})' # Name of the edge variable
                    add_to_mapping(epsilon) # Add to mapping (if not already there)
                    
                    all_outgoing_edges.append(epsilon) # Add to list of outgoing edges for T1 purpose
                    incoming_edges_map[v_child.index].append(epsilon) # Add to incoming edges map
                    
                    x_i = f'x_{v_i.variable_index} = {j}th value' # Name of the variable that represents the value of the node v_i = j
                    add_to_mapping(x_i) # Add to mapping (if not already there)
                    
                    self.mapping_variable_xval[v_i.variable_name].add(x_i) # Add to variable names to x_i = j map
                    variable_values_edges_map[x_i].append(epsilon) # Add to variable values edges map
                    
                    # Following clauses are added to the cnf formula (Tseitin encoding) 
                    
                    # T2: epsilon -> v_i
                    self.cnf.append([-self.mapping[epsilon], self.mapping[v_i]]) 

                    # T3: epsilon -> v_child
                    self.cnf.append([-self.mapping[epsilon], self.mapping[v_child]])
                    
                    # T4: epsilon -> x_i = j
                    self.cnf.append([-self.mapping[epsilon], self.mapping[x_i]])
                    
                    
                    # P1: v_i and x_ji -> epsilon
                    self.cnf.append([-self.mapping[v_i], -self.mapping[x_i], self.mapping[epsilon]])
                    
                # T1: v_i -> V_j epsilon_j
                self.cnf.append([-self.mapping[v_i]] + [self.mapping[epsilon] for epsilon in all_outgoing_edges])
                
                # Modification
                # Add at most one constraint for the outgoing edges
                if len(all_outgoing_edges) > 1:
                    exactly_one_encoding = self.at_most_one([self.mapping[epsilon] for epsilon in all_outgoing_edges])
                    for clause in exactly_one_encoding:
                        self.cnf.append(clause)
        
        
        # P2: v_i -> exists epsilon_(i-1)_i \ where i != 1 (i.e. not root node)
        for i in sorted(odd.keys()):
            v_i = odd[i]
            if i != 1:
                logging.debug(f'Adding P2 for node {v_i.variable_name}: {[-self.mapping[v_i]] + [self.mapping[inc_edge] for inc_edge in incoming_edges_map[v_i.index]]}')
                self.cnf.append([-self.mapping[v_i]] + [self.mapping[inc_edge] for inc_edge in incoming_edges_map[v_i.index]])    
        
        # P3: x_ij -> epsilon_i_j
        for x, epsilons in variable_values_edges_map.items():
            self.cnf.append([-self.mapping[x]] + [self.mapping[epsilon] for epsilon in epsilons])
            
        
        for i in sorted(odd.keys()): # For all nodes in the ODD
            v_i  = odd[i]
            if v_i.edges:
                for j, v_child_index in enumerate(v_i.edges):
                    # T5: v_child and x_i = j -> epsilon
                    x_i = f'x_{v_i.variable_index} = {j}th value' 
                    v_child = odd[v_child_index]
                    self.cnf.append([-self.mapping[v_child], -self.mapping[x_i]] + [self.mapping[epsilon] for epsilon in incoming_edges_map[v_child.index]])
        
        # # P4: ExactlyOne(v for v in odd_nodes_on_level_i)
        levels = defaultdict(list)
        for i in sorted(odd.keys()):
            levels[odd[i].variable_index].append(odd[i])
            
        for level in levels.values():
            if len(level) > 1: 
                literals = [self.mapping[v] for v in level]
                exactly_one_encoding = self._exactly_one(literals)
                for clause in exactly_one_encoding:
                    self.cnf.append(clause)
        
        return self.cnf, self.mapping, self.mapping_inv

if __name__ == '__main__':    
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert ODD to CNF')
    
    parser.add_argument('--odd', type=str, help='Path to the ODD file')
    parser.add_argument('--cnf', type=str, help='Path to the CNF file')
    parser.add_argument('--verbose', action='store_true', help='Print info messages')
    parser.add_argument('--debug', action='store_true', help='Print debug messages')
    
    odd_path = parser.parse_args().odd
    cnf_path = parser.parse_args().cnf
    verbose = parser.parse_args().verbose
    debug = parser.parse_args().debug
    
    # Set logging level
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    if '.odd' not in odd_path:
        odd_path += '.odd'
    if '.json' not in cnf_path:
        cnf_path += '.json'
    
    odd = read_obdd_from_file(f'{odd_path}')
    
    encoder = TseitinEncoder()
    _cnf, _map, _map_inv = encoder.encode_to_cnf(odd)
    
    encoder.save_to_json(cnf_path)
    
 
    logging.debug(_cnf.clauses)
    
    print_mapping(_map_inv)
    
    print_with_names(_cnf, _map_inv)
    
    should_SAT = PySATSolver().solve(_cnf, assumptions=[])
    assert should_SAT, "Should be SAT"
    logging.info('SAT for empty assumptions')
    
    logging.debug('----SAT MODEL--'*10)
    s = ''
    for i in should_SAT:
        if i > 0:
            s += f'{i}: {_map_inv[i]}, \n'
    logging.info(f'Variables set to TRUE in the model: \n{s}')
    
    should_UNSSAT = PySATSolver().solve(_cnf, assumptions=[-1])
    assert not should_UNSSAT, "Should be UNSAT"
    logging.info('UNSAT for assumption where root node is false')