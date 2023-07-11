from typing import List, Tuple

def tseitin_transformation_2(dnf: List[List[int]], max_var: int) -> List[List[int]]:
    '''
    Convert DNF to CNF using Tseitin transformation.
    Constraint is that each clause in DNF has exactly 2 literals.
    
    Example:
        DNF: [[1, 2], [3, 4], [5, 6]]
    '''
    max_var += 1
    
    dnf, cnf = tseitin_transform_neg(dnf, max_var)
    
    # First, for each clause in DNF, we need to create a new variable.
    # And rewrite the clause in CNF.
    cnf.append([max_var + i for i in range(len(dnf))])
    
    for i, dnf_clause in enumerate(dnf):
        # rewrite and as a CNF.
        cnf.append([dnf_clause[0], -max_var])
        cnf.append([dnf_clause[1], -max_var])
        cnf.append([-dnf_clause[0], -dnf_clause[1], max_var])
        
        max_var += 1
            
    return cnf

def tseitin_transform_neg(dnf: List[List[int]], max_var: int) -> Tuple[List[List[int]], List[List[int]]]:
    '''
    Supplementary function for tseitin_transformation_2.
    Transform all negations in formula to positive literals.
    Using tsitin transformation.
    
    Return:
        dnf: transformed dnf
        cnf: tseitin transformation clauses
    '''
    
    already_added = dict()
    cnf = []
    
    for i, clause in enumerate(dnf):
        for j, literal in enumerate(clause):
            if literal < 0 and abs(literal) not in already_added:
                dnf[i][j] = max_var
                max_var += 1
                cnf.append([abs(literal), max_var])
                cnf.append([-abs(literal), -max_var])
                already_added[abs(literal)] = max_var
            elif literal < 0 and abs(literal) in already_added:
                dnf[i][j] = already_added[abs(literal)]
    
    return dnf, cnf
            
                