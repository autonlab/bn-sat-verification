# Encode OMDD (Ordered Multivalue Decision Diagram) to a CNF (Conjunctive Normal Form) formula
# Using the Tseitin encoding method
# Based on paper: "On CNF Encodings of Decision Diagrams"
from node import Node
from shih_to_obdd import read_obdd_from_file, draw_obdd
from typing import Dict, List, Tuple
from pysat.formula import CNF
from pysat_solver import pysat_solver

MODELPATH = "odd_models/admission/admission1_1.odd"
CLAUSES = []

def add_node_clauses(clauses: List, odd: Dict[int, Node]) -> Tuple[CNF, Dict, Dict]:
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
        
        if odd[i].variable_name == "TRUE":
            # True leaf node, add clause that it is true
            cnf.append([mapping[v_i]])
            continue
        if odd[i].variable_name == "FALSE":
            # False leaf node, add clause that it is false
            cnf.append([-mapping[v_i]])
            continue
        
        for j, v_child_index in enumerate(v_i.edges): # For all edges of the node v_i
            v_child = odd[v_child_index] # Node at level i+1, to which the edge j of v_i leads to
            add_to_mapping(v_child) # Add to mapping (if not already there)
            
            all_outgoing_edges.append(v_child) # Add to list of outgoing edges for T1 purpose
            
            epsilon = f'edge_{v_i.variable_name}_{v_child.variable_name}' # Name of the edge variable
            add_to_mapping(epsilon) # Add to mapping (if not already there)
            
            x_i = f'x_{v_i.variable_name} = {j}th value' # Name of the variable that represents the value of the node v_i = j
            add_to_mapping(x_i) # Add to mapping (if not already there)
            
            # Following clauses are added to the cnf formula (Tseitin encoding) 
            
            # T2: epsilon -> v_i
            cnf.append([-mapping[epsilon], mapping[v_i]]) 

            # T3: epsilon -> v_child
            cnf.append([-mapping[epsilon], mapping[v_child]])
            
            # T4: epsilon -> x_i = j
            cnf.append([-mapping[epsilon], mapping[x_i]])
            
            # T5: v_child and x_i = j -> epsilon
            cnf.append([-mapping[v_child], -mapping[x_i], mapping[epsilon]])
            
        # T1: v_i -> V_j epsilon_j
        cnf.append([-mapping[v_i]] + [mapping[epsilon] for epsilon in all_outgoing_edges])
        
    return cnf, mapping, mapping_inv
    
def print_with_names(cnf: CNF, mapping_inv: Dict):
    '''
    Print the cnf formula with the names of the variables
    '''
    for clause in cnf.clauses:
        print([mapping_inv[abs(lit)] if lit > 0 else f'-{mapping_inv[abs(lit)]}' for lit in clause])

def print_mapping(mapping: Dict):
    '''
    Print the mapping in a nice way
    '''
    for key, value in mapping.items():
        print(f'{key:{" "}{"<"}{3}}: {value}')



if __name__ == '__main__':
    # -------------------------------
    # This is the example that encodes following OBDD
    #                        0 --> False
    #   0 --> WorkExperience 1 --> True 
    # GPA
    #   1 --> WorkExperience 1 --> True
    #                        0 --> False
    # -------------------------------
    
    gpa = Node(0, 0, 1, 2, "GPA")
    we_1 = Node(1, 1, 3, 4, "WE_1")
    we_2 = Node(2, 2, 3, 4, "WE_2")
    ter_t = Node(3, 3, None, None, "TRUE")
    ter_f = Node(4, 4, None, None, "FALSE")
    
    odd = {
        0: gpa,
        1: we_1,
        2: we_2,
        3: ter_t,
        4: ter_f
    }
    
    _cnf, _map, _map_inv = add_node_clauses(CLAUSES, odd)
 
    print(_cnf.clauses)
    
    print_mapping(_map_inv)
    
    print('\n\n')
    
    print_with_names(_cnf, _map_inv)
    
    should_SAT = pysat_solver(_cnf, set_variables=[1, 5, 6, 7, 8, -11, 14, 15])
    assert should_SAT, "Should be SAT"
    
    should_UNSSAT = pysat_solver(_cnf, set_variables=[1, 5, 6, 7, 8, -11, 16, 17])
    assert not should_UNSSAT, "Should be UNSAT"