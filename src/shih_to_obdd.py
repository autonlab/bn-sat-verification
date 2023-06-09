import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os

from typing import Tuple, Dict, List


class Node:
    def __init__(self, ordering_index: int, variable_index: int, left: int, right: int, variable_name: str) -> None:
        self.index = ordering_index
        self.variable_index = variable_index
        self.left = left
        self.right = right
        self.variable_name = variable_name
    
    def __str__(self) -> str:
        return f"Node_{self.index:{' '}{'<'}{5}} Left: {self.left:{' '}{'<'}{3}} \
          Right: {self.right:{' '}{'<'}{3}} VarIndex: \"{self.variable_index:{' '}{'<'}{2}}\" \
            VarName: \"{self.variable_name:{' '}{'<'}{3}}"

    def __repr__(self) -> str:
        return self.__str__()
        
def read_obdd_from_file(filename: str) -> Tuple[Dict[int, Node], List[str]]:
    '''Reads in an OBDD from a file and returns a dictionary of nodes and a list of variable names'''
    with open(filename,'r') as f:
        variable_names = f.readline().replace('[', '').replace(',', '') \
            .replace(']', '').strip().split(' ')
        print(variable_names)
        nodes = f.readlines()
        nodes = [x.strip().split(' ') for x in nodes]
        nodes = [[int(x) if x.isdigit() else x for x in node] for node in nodes]  

    node_dict = {}
    for l in nodes:
        node_dict[l[0]] = Node(l[0], l[1], l[2], l[3], variable_names[l[1]])

    return node_dict

def prettyprint_dict(node_dict: Dict[int, Node]) -> None:
    '''Prints out the dictionary of nodes in a pretty format'''
    for key in sorted(node_dict):
        print(node_dict[key])
    

def draw_obdd(node_dict: Dict[int, Node]) -> None:
    '''Draws the OBDD using networkx. The nodes are labeled with their variable names'''
    G = nx.DiGraph()
    labeldict = {k:v.variable_name for k,v in node_dict.items()}
    labeldict['S0'] = 'S0'
    labeldict['S1'] = 'S1'

    for key in sorted(node_dict):
        G.add_node(node_dict[key].index, name=node_dict[key].variable_name)
        G.add_edge(node_dict[key].index, node_dict[key].left)
        G.add_edge(node_dict[key].index, node_dict[key].right)
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