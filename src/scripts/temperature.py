import pysmile
import pysmile_license as pysmile_license
from pysmile_utils import *

SAVEDIR = 'models'

net = pysmile.Network()

# ------ Nodes -----------------------
create_cpt_node(net, 
                'Temperature', 
                'Temperature level', 
                ['Low', 'High'], 
                10, 
                10)

create_cpt_node(net,
                'Heatstroke',
                'Have Heatstroke',
                ['No', 'Light', 'Severe'],
                15,
                15)

create_cpt_node(net,
                'WearingHat',
                'WearingHat',
                ['False', 'True'],
                20,
                20)
# ------------------------------------

# ------ Marginal Probabilities ------
temp_base_prob_distr = [
    0.7, 0.3
]
# ------------------------------------

# ------ CPT ------
heatsroke_CPT = [
#   No      Light   Severe   variable 
    0.88,    0.4,    0.1,   # Low Y temperature
    0.12,    0.6,    0.9    # High Y temperature
]

wearHat_CPT = [
#   False   True wearing hat
    0.85,    0.3, # Low Y Temperature
    0.15,    0.7, # High Y Temperature
]
# -----------------

# ------ Arcs ------
net.add_arc('Temperature', 'Heatstroke')
net.add_arc('Temperature', 'WearingHat')
# ------------------

# ------ Wiring up the node with the marginal probabilities ------
net.set_node_definition('Temperature', temp_base_prob_distr)
net.set_node_definition('Heatstroke', heatsroke_CPT)
net.set_node_definition('WearingHat', wearHat_CPT)
# ----------------------------------------------------------------

net.write_file(f"{SAVEDIR}/temperature.xdsl")

# ------ Evidence ------
print("Setting WearingHat=False.")
change_evidence_and_update(net, "WearingHat", "True")

print("Setting Heatstroke=False.")
change_evidence_and_update(net, "Heatstroke", "Light")
# ----------------------

# ------ Posterior ------
# print(get_node_posteriors(net, "Temperature"))
print(check_if_node_is_evidence(net, "Temperature"))

print("Posterior: ")
print_all_posteriors(net)
# -----------------------



