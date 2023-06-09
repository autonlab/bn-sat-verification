import pysmile
from typing import List, Tuple

def create_cpt_node(net: pysmile.Network, 
                    id: str, 
                    name: str, 
                    outcomes: List[str], 
                    x_pos: int, 
                    y_pos: int):
    
    handle = net.add_node(pysmile.NodeType.CPT, id)
    
    net.set_node_name(handle, name)
    net.set_node_position(handle, x_pos, y_pos, 85, 55)
    
    initial_outcome_count = net.get_outcome_count(handle)
    
    for i in range(0, initial_outcome_count):
        net.set_outcome_id(handle, i, outcomes[i])
    
    for i in range(initial_outcome_count, len(outcomes)):
        net.add_outcome(handle, outcomes[i])
        
    return handle

def print_posteriors(net: pysmile.Network, node_handle: int | str) -> None:
    node_id = net.get_node_id(node_handle)
    if net.is_evidence(node_handle):
        print(node_id + " has evidence set (" +
                net.get_outcome_id(node_handle, 
                                    net.get_evidence(node_handle)) + ")")
    else :
        posteriors = net.get_node_value(node_handle)
        for i in range(0, len(posteriors)):
            print("P(" + node_id + "=" + 
                    net.get_outcome_id(node_handle, i) +
                    ")=" + str(posteriors[i]))

def print_all_posteriors(net: pysmile.Network) -> None:
    for handle in net.get_all_nodes():
        print_posteriors(net, handle)
        

def change_evidence_and_update(net: pysmile.Network, node_id: int | str, outcome_id: int | str) -> None:
        if outcome_id is not None:
            net.set_evidence(node_id, outcome_id)	
        else:
            net.clear_evidence(node_id)
        
        net.update_beliefs()
        
def get_all_node_ids(net: pysmile.Network) -> List[str]:
    '''Returns a list of all node ids in the network. IDs are name-strings.'''
    return net.get_all_node_ids()
    
def get_node_posteriors(net: pysmile.Network, nodeID: str) -> List[Tuple[str, float]]:
    '''Returns a list of tuples of the form (outcome, posterior) for the given nodeID.'''
    posteriors = net.get_node_value(nodeID)
    outcomes = net.get_outcome_ids(nodeID)
    return list(zip(outcomes, posteriors))

def check_if_node_is_evidence(net: pysmile.Network, nodeID: str) -> bool:
    '''Returns True if the node is evidence in the network, False otherwise.'''
    return net.is_evidence(nodeID)
