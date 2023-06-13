import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import logging

from typing import Tuple, Dict, List
        
from node import Node    


def read_obdd_from_file(filename: str) -> Dict[int, Node]:
    '''Reads in an OBDD from a file and returns a dictionary of nodes and a list of variable names'''
    with open(filename,'r') as f:
        variable_names = f.readline().replace('[', '').replace(',', '') \
            .replace(']', '').strip().split(' ')
        logging.debug(variable_names)
        nodes = f.readlines()
        nodes = [x.strip().split(' ') for x in nodes]
        nodes = [[int(x) if x.isdigit() else x for x in node] for node in nodes]  
        
        numbers = set(x for node in nodes for x in node if isinstance(x, int))
    
    # Reindexing the nodes to start from 1 and increment by 1
    translate_indices = {x: i + 1 for i, x in enumerate(sorted(numbers))} 
    last = max(translate_indices.values())
    translate_indices['S1'] = last + 1
    translate_indices['S0'] = last + 2
    
    node_dict = {}
    for ordering_index, variable_index, left, right  in nodes:
        ordering_index = translate_indices[ordering_index]
        variable_index = translate_indices[variable_index]
        left = translate_indices[left]
        right = translate_indices[right]
        node_dict[ordering_index] = Node(ordering_index, variable_index, left, right, variable_names[variable_index - 1])
        
    # Add the sinks
    node_dict[last + 1] = Node(last + 1, None, None, None, 'TRUE')
    node_dict[last + 2] = Node(last + 2, None, None, None, 'FALSE')
        
    return node_dict

def prettyprint_dict(node_dict: Dict[int, Node]) -> None:
    '''Prints out the dictionary of nodes in a pretty format'''
    for key in sorted(node_dict):
        logging.debug(node_dict[key])
    

def draw_obdd(node_dict: Dict[int, Node]) -> None:
    '''Draws the OBDD using networkx. The nodes are labeled with their variable names'''
    G = nx.DiGraph()
    labeldict = {k:v.variable_name for k,v in node_dict.items()}

    for key in sorted(node_dict):
        G.add_node(node_dict[key].index, name=node_dict[key].variable_name, pos='mid')
        if node_dict[key].edges[0] is not None:
            G.add_edge(node_dict[key].index, node_dict[key].edges[0], pos='left')
        if node_dict[key].edges[1] is not None:
            G.add_edge(node_dict[key].index, node_dict[key].edges[1], pos='right')
    pos = nx.spring_layout(G)

    fig = plt.figure(figsize=(8, 8))
    nx.draw(G, pos, with_labels=True, labels=labeldict, node_size=700, font_size=8)
    plt.show()


if __name__ == '__main__':
    # Initialize the parser
    parser = argparse.ArgumentParser(description='Parses an OBDD from a file and creates a graph structure')
    parser.add_argument('--filepath', type=str, help='The filename with path of the OBDD to be parsed')
    parser.add_argument('--plot', type=bool, default=True, help='Whether to plot the OBDD')
    parser.add_argument('--verbose', action='store_true', help='Whether to print debug messages')
    
    if parser.parse_args().verbose:
        logging.basicConfig(level=logging.DEBUG)
    else: 
        logging.basicConfig(level=logging.WARNING)
    
    # Make sure the filepath is provided correctly
    filepath = parser.parse_args().filepath
    if filepath is None:
        raise ValueError('Please provide a filepath to the OBDD file')
    if not os.path.exists(filepath):
        raise ValueError('The provided filepath does not exist')
    if not filepath.endswith('.odd'):
        filepath += '.odd'    
    
    dic = read_obdd_from_file(filepath)
    prettyprint_dict(dic)
    
    if parser.parse_args().plot:    
        draw_obdd(dic)