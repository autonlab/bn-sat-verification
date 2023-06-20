from typing import List

def tseitin_transformation_2(dnf: List[List[int]], max_var: int) -> List[List[int]]:
    '''
    Convert DNF to CNF using Tseitin transformation.
    Constraint is that each clause in DNF has exactly 2 literals.
    
    Example:
        DNF: [[1, 2], [3, 4], [5, 6]]
    '''
    max_var += 1
    
    # First, for each clause in DNF, we need to create a new variable.
    # And rewrite the clause in CNF.
    cnf = []
    cnf.append([max_var + i for i in range(len(dnf))])
    
    for i, dnf_clause in enumerate(dnf):
        # rewrite and as a CNF.
        cnf.append([dnf_clause[0], -max_var])
        cnf.append([dnf_clause[1], -max_var])
        cnf.append([-dnf_clause[0], -dnf_clause[1], max_var])
        
        max_var += 1
            
    return cnf