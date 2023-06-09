import pysmile
import pysmile_license
from pysmile_utils import *
import argparse
import numpy as np

def convert_to_shih(input_file: str, output_file: str) -> str:
    '''
    Convert a BayesFusion xdsl BN to the Shih's format. 
    
    Return path to the converted file.
    '''
    net = pysmile.Network()
    net.clear_all_evidence()
    net.update_beliefs()
    net.read_file(input_file)
    
    with open(output_file, 'w') as f:        
        # Write empty net?
        f.write('net\n{\n}\n')
        
        # Iterate over all nodes
        for node_id in get_all_node_ids(net):
            # Extract the outcomes for this node
            outcomes = net.get_outcome_ids(node_id)
            
            f.write('node ' + node_id + '\n' + '{\n' + 'states = ( "' + '" "'.join(outcomes) + '" );\n}\n')
                
        # Iterate over all nodes
        for node_id in get_all_node_ids(net):
            
            net.clear_all_evidence() # idk why this is needed but it is
            net.update_beliefs() # same here
            
            node_outcomes = net.get_outcome_ids(node_id)
            values = net.get_node_definition(node_id)
            parents = net.get_parent_ids(node_id)
            
            # now we need to form the CPT in Shih's format
            # I believe the order is like follows:
            # (Xn, Xn-1, ..., X2, X1, Classes)
            # e.g., GoodStudent (Class = 2 outcomes) | SocioEcon (X2 = 4 outcomes) Age (X1 = 3 outcomes)
            # potential ( GoodStudent | SocioEcon Age ) 
            # {
            # data = (
            #     ((0.1 0.9)(0.0 1.0)(0.0 1.0))
            #     ((0.2 0.8)(0.0 1.0)(0.0 1.0))
            #     ((0.5 0.5)(0.0 1.0)(0.0 1.0))
            #     ((0.4 0.6)(0.0 1.0)(0.0 1.0))
            #     ) 
            #     ;
            # }
            # Shape in Shih's format looks like 4,3,2 in this case 
            
            # Our order of values in CPT is I think the same but flattened?
            # TODO check this
            
            dimensions = []
            for parent in parents:
                dimensions.append(len(net.get_outcome_ids(parent)))
            
            # Build shih's cpt
            shih_cpt_shape = dimensions + [len(node_outcomes)]
            shih_cpt = np.array(values)
            shih_cpt = shih_cpt.reshape(shih_cpt_shape) # TODO check this, but seems to work
            
            print(shih_cpt_shape)
            print(shih_cpt)
            
            # Now we need to write this to the file in the correct format
            
            f.write('potential ( ' + node_id + ' | ' + ' '.join(parents) + ' )\n{\n')
            f.write('data = (\n')
            
            def __write_shih_cpt_recursively(cpt, dimensions, current_dimension, f):
                if current_dimension == len(dimensions):
                    f.write('(' + ' '.join([str(x) for x in cpt]) + ')')
                    return
                f.write('(')
                
                for i in range(dimensions[current_dimension]):
                    __write_shih_cpt_recursively(cpt[i], dimensions, current_dimension + 1, f)
                    
                f.write(')')
                    
            __write_shih_cpt_recursively(shih_cpt, dimensions, 0, f)
            
            f.write(') ;\n}\n')
            
            

           
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a BayesFusion xdsl BN to the Shih\'s format.')
    parser.add_argument('--input_file', type=str, help='Path to the input file')
    parser.add_argument('--output_file', type=str, help='Path to the output file')
    args = parser.parse_args()
    
    convert_to_shih(args.input_file, args.output_file)
            
    
