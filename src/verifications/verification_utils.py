from pysat.formula import CNF
from typing import Dict, List, Tuple
from utils.tseitin_transformation import tseitin_transformation_2



def strip_sinks(cnf: CNF, sinks_map: dict, mapping: dict) -> CNF:
    altered_cnf = []
    for clause in cnf.clauses:
        # Remove sink constraints that say TRUE sink has to be true 
        # and FALSE sink has to be false. We want to check if any 
        # assignment from verification query is possible. 
        # We do not lose soundness of the entire enocoding,
        # as we have clauses that disallow True and False to be
        # active at the same time
        drop = False
        for true_sink, false_sink in sinks_map:
            t = int(mapping[true_sink])
            f = int(mapping[false_sink])
            if clause == [t] or clause == [-t] or clause == [f] or clause == [-f]:
                drop = True
        
        # If not drop then we just add clause to the goal cnf
        if not drop:
            altered_cnf.append(clause)  
            
    return CNF(from_clauses=altered_cnf)

def A_greater_than_B(a: List[int], b: List[int], max_var):
    '''
    Returns CNF clauses that encode the constraint a > b.
    
    Parameters
        `a`: List of integers that represent literals in A. 
        They are assumed to be sorted in ascending ordinal order.
        
        `b`: List of integers that represent literals in B.
        They are assumed to be sorted in ascending ordinal order.
        
        `max_var`: Maximum variable in the formula.
    '''
    dnf = []
    for i in range(len(a)):
        for j in range(len(b)):
            if i > j:
                dnf.append([a[i], b[j]])
    return tseitin_transformation_2(dnf, max_var)    
    
                