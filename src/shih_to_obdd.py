import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os

from typing import Tuple, Dict, List
        
from node import Node

def read_obdd_from_file(filename: str) -> Dict[int, Node]:
    '''Reads in an OBDD from a file and returns a dictionary of nodes and a list of variable names'''
    with open(filename,'r') as f:
        variable_names = f.readline().replace('[', '').replace(',', '') \
            .replace(']', '').strip().split(' ')
        print(variable_names)
        nodes = f.readlines()
        nodes = [x.strip().split(' ') for x in nodes]
        nodes = [[int(x) + 1 if x.isdigit() else x for x in node] for node in nodes]  
        

    node_dict = {}
    for l in nodes:
        node_dict[l[0]] = Node(l[0], l[1], l[2], l[3], variable_names[l[1] - 1])

    return node_dict

def prettyprint_dict(node_dict: Dict[int, Node]) -> None:
    '''Prints out the dictionary of nodes in a pretty format'''
    for key in sorted(node_dict):
        print(node_dict[key])
    

def draw_obdd(node_dict: Dict[int, Node]) -> None:
    '''Draws the OBDD using networkx. The nodes are labeled with their variable names'''
    G = nx.DiGraph()
    labeldict = {k:v.variable_name for k,v in node_dict.items()}
    # labeldict['S0'] = 'S0'
    # labeldict['S1'] = 'S1'

    for key in sorted(node_dict):
        G.add_node(node_dict[key].index, name=node_dict[key].variable_name)
        if node_dict[key].edges[0] is not None:
            G.add_edge(node_dict[key].index, node_dict[key].edges[0])
        if node_dict[key].edges[1] is not None:
            G.add_edge(node_dict[key].index, node_dict[key].edges[1])
    pos = nx.spring_layout(G)

    fig = plt.figure(figsize=(8, 8))
    nx.draw(G, pos, with_labels=True, labels=labeldict, node_size=700, font_size=8)
    plt.show()


if __name__ == '__main__':
    # Initialize the parser
    parser = argparse.ArgumentParser(description='Parses an OBDD from a file and creates a graph structure')
    parser.add_argument('--filepath', type=str, help='The filename with path of the OBDD to be parsed')
    parser.add_argument('--plot', type=bool, default=True, help='Whether to plot the OBDD')
    
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