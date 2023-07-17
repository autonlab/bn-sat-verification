from typing import List, Tuple

def tseitin_transformation_2(dnf: List[List[int]], max_var: int) -> Tuple[List[List[int]], int]:
    '''
    Convert DNF to CNF using Tseitin transformation.
    Constraint is that each clause in DNF has exactly 2 literals.
    
    Example:
        DNF: [[1, 2], [3, 4], [5, 6]]
        
    Return:
        CNF: cnf clauses that encode the same constraint as DNF.
        max_var: maximum variable in the formula
    '''
    max_var += 1
    
    dnf, cnf, max_var = tseitin_transform_neg(dnf, max_var)
    
    # First, for each clause in DNF, we need to create a new variable.
    # And rewrite the clause in CNF.
    cnf.append([max_var + i for i in range(len(dnf))])
    
    for i, dnf_clause in enumerate(dnf):
        # rewrite and as a CNF.
        cnf.append([dnf_clause[0], -max_var])
        cnf.append([dnf_clause[1], -max_var])
        cnf.append([-dnf_clause[0], -dnf_clause[1], max_var])
        
        max_var += 1
            
    return cnf, max_var - 1

def tseitin_transform_neg(dnf: List[List[int]], max_var: int) -> Tuple[List[List[int]], List[List[int]], int]:
    '''
    Supplementary function for tseitin_transformation_2.
    Transform all negations in formula to positive literals.
    Using tsitin transformation.
    
    Return:
        dnf: transformed dnf
        cnf: tseitin transformation clauses
        max_var: maximum variable in the formula + 1
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
    
    return dnf, cnf, max_var
            
            
def tseitin_transformation(dnf: List[List[int]], start_var: int) -> Tuple[List[List[int]], int]:
    '''
    Convert DNF to CNF using Tseitin transformation.
    
    Input format is a list of lists of integers.
    Function should be able to handle any number of literals in each clause (with negations).
    
    Note, that this function does not check if the input is a valid DNF.
    Also, NEG before AND before OR is not allowed. You can only have NEG before particular literal.
    
    Input:
        dnf: list of lists of integers. Each list is a clause in DNF.
        start_var: maximum variable in the formula + 1
        
    Return:
        cnf: cnf clauses that encode the same constraint as DNF.
        max_var: maximum variable in the formula
    
    '''
    # Parse from left to right linearly
    
    cnf = []
    
    # For simplicity, get rid of negations first
    for i, clause in enumerate(dnf):
        for j, literal in enumerate(clause):
            if literal < 0:
                # NEG tseitin transformation
                t = start_var
                start_var += 1
                cnf.append([literal, t])
                cnf.append([-literal, -t])
                
                dnf[i][j] = t
    
    DNF_ONE = []
    for clause in dnf:
        last_t = clause[0]
        
        for i in range(1, len(clause)):
            # AND tseitin transformation
            new_t = start_var
            start_var += 1
            
            cnf.append([-last_t, -clause[i], new_t])
            cnf.append([last_t, -new_t])
            cnf.append([clause[i], -new_t])
            
            # Update last_t
            last_t = new_t
            
        DNF_ONE.append(last_t)
            
    
    # OR tseitin transformation
    for i in range(1, len(DNF_ONE)):
        new_t = start_var
        start_var += 1
        
        cnf.append([DNF_ONE[i - 1], DNF_ONE[i], -new_t])
        cnf.append([-DNF_ONE[i - 1], new_t])
        cnf.append([-DNF_ONE[i], new_t])
        
    return cnf, start_var - 1



if __name__ == '__main__':
    
    # Verify tseitin transformation
    dnf = [[-1, 2, 3], [1,2]]
    cnf, max_var = tseitin_transformation(dnf, 4)
    print(cnf)