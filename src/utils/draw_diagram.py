import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict
from utils.node import Node

def draw_obdd(node_dict: Dict[int, Node], 
              coloring_dict: Dict[str, str] = {}, 
              title: str = '',
              display_block: bool = True,
              ) -> None:
    '''Draws the OBDD using networkx. The nodes are labeled with their variable names'''
    G = nx.DiGraph()
    labeldict = {k:v.variable_name for k,v in node_dict.items()}
    max_level = max([v.variable_index for _,v in node_dict.items()])

    for i, key in enumerate(sorted(node_dict, reverse=False)):
        
        # Set the y position/level of the nodes
        level = node_dict[key].variable_index
        if level == -999:
            level = 0
            if node_dict[key].variable_name == 'TRUE':
                color = 'green'
            else:
                color = 'lightcoral'
        else:
            level = max_level + 1 - level
            color = 'steelblue' if level % 2 == 0 else 'skyblue'
            
        color = match_node_names_to_actual_nodes(node_dict[key], coloring_dict, color)

        # Add the nodes    
        G.add_node(node_dict[key].index, 
                   name=node_dict[key].variable_name, 
                   pos='mid',
                   level=level,
                   color=color,)
        
        # Add the edges
        if node_dict[key].edges:
            for j, edge in enumerate(node_dict[key].edges):
                G.add_edge(node_dict[key].index, edge, 
                           label=f'{node_dict[key].variable_name}_{node_dict[key].index}_{j}',
                           color=match_edge_name_to_actual_edge(node_dict[key].index, edge, coloring_dict),
                )
                
    pos = nx.multipartite_layout(G, subset_key="level", align='horizontal')
    
    edge_colors = [G[u][v]['color'] for u,v in G.edges]

    fig = plt.figure(figsize=(8, 8))
    nx.draw(G, 
            pos=pos, 
            with_labels=True, 
            labels=labeldict, 
            node_size=2000, 
            font_size=10, 
            node_color=[G.nodes[n]['color'] for n in G.nodes],
            edge_color=edge_colors,
            )
    
    nx.draw_networkx_edge_labels(G, 
                                 pos=pos, 
                                 edge_labels=nx.get_edge_attributes(G, 'label'), 
                                 font_size=8.5)
    
    plt.show(block=display_block)
    
def match_node_names_to_actual_nodes(node: Node, coloring_dict: Dict[str, str], color: str) -> str:
    '''
    Matches the node names to the actual nodes in the OBDD.
    '''  
    n = f'Node_{node.variable_name}_{node.index}'
    if n in coloring_dict:
        return coloring_dict[n]
    
    return color

def match_edge_name_to_actual_edge(outgoing_index: int, incoming_index: int, coloring_dict: Dict[str, str]) -> str:
    '''
    Matches the edge names to the actual edges in the OBDD.
    ''' 
    for key in coloring_dict:
        if f'edge_{outgoing_index}_{incoming_index}' in key:
            return coloring_dict[key]
    
    return 'black'