import pysmile
import scripts.pysmile_license as pysmile_license
from scripts.pysmile_utils import *

SAVEDIR = 'models'

net = pysmile.Network()

# ------ Nodes -----------------------
create_cpt_node(net, 
                'Admit', 
                'Admission', 
                ['True', 'False'], 
                10, 
                10)

create_cpt_node(net,
                'WorkExperience',
                'Work Experience',
                ['True', 'False'],
                15,
                15)

create_cpt_node(net,
                'GPA',
                'GPA',
                ['True', 'False'],
                20,
                20)
# ------------------------------------

# ------ Marginal Probabilities ------
admit_prob_dist = [
    0.7, 0.3
]
# ------------------------------------

# ------ CPT ------
workexperiecnce_hat_CPT = [
    0.9,
    0.04,
    0.1,
    0.96,
]

gpa_CPT = [
    0.89,
    0.03,
    0.1,
    0.97,
]
# -----------------

# ------ Arcs ------
net.add_arc('Admit', 'WorkExperience')
net.add_arc('Admit', 'GPA')
# ------------------

# ------ Wiring up the node with the marginal probabilities ------
net.set_node_definition('Admit', admit_prob_dist)
net.set_node_definition('WorkExperience', workexperiecnce_hat_CPT)
net.set_node_definition('GPA', gpa_CPT)
# ----------------------------------------------------------------

net.write_file(f"{SAVEDIR}/admission1.xdsl")

# ------ Evidence ------
print("Setting GPA=False.")
change_evidence_and_update(net, "GPA", "True")

print("Setting WorkExperience=False.")
change_evidence_and_update(net, "WorkExperience", "False")
# ----------------------

# ------ Posterior ------
# print(get_node_posteriors(net, "Admit"))
print(check_if_node_is_evidence(net, "Admit"))

print("Posterior: ")
print_all_posteriors(net)
# -----------------------



