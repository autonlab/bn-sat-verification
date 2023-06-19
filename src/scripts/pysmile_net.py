import pysmile
import pysmile_license
from pysmile_utils import *

SAVEDIR = 'models'

net = pysmile.Network()

# ------ Nodes -----------------------
weather_handle = create_cpt_node(net, 
                'Weather', 
                'Current weather outside', 
                ['Hot', 'Moderate', 'Cold'], 
                10, 
                10)

wearing_hat_handle = create_cpt_node(net,
                                    'WearingHat',
                                    'Is the person wearing a hat?',
                                    ['Yes', 'No'],
                                    15,
                                    15)

heatstroke_handle = create_cpt_node(net,
                                    'Heatstroke',
                                    'Is it likely to get heatstroke?',
                                    ['Yes', 'No'],
                                    20,
                                    20)
# ------------------------------------

# ------ Marginal Probabilities ------
weather_prob_dist = [
    0.6, # P(Weather = Hot)
    0.3, # P(Weather = Moderate)
    0.1  # P(Weather = Cold)
]
# ------------------------------------

# ------ CPT ------
wearing_hat_CPT = [
    0.8, # P(WearingHat = Yes | Weather = Hot )
    0.2, # P(WearingHat = No | Weather = Hot )
    0.5, # P(WearingHat = Yes | Weather = Moderate )
    0.5, # P(WearingHat = No | Weather = Moderate )
    0.1, # P(WearingHat = Yes | Weather = Cold )
    0.9, # P(WearingHat = No | Weather = Cold )
]

heatstroke_CPT = [
    0.7, # P(Heatstroke = Yes | Weather = Hot, WearingHat = Yes)
    0.3, # P(Heatstroke = No | Weather = Hot, WearingHat = Yes)
    
    0.8, # P(Heatstroke = Yes | Weather = Hot, WearingHat = No)
    0.2, # P(Heatstroke = No | Weather = Hot, WearingHat = No)
    
    0.1, # P(Heatstroke = Yes | Weather = Moderate, WearingHat = Yes)
    0.9, # P(Heatstroke = No | Weather = Moderate, WearingHat = Yes)

    0.12, # P(Heatstroke = Yes | Weather = Moderate, WearingHat = No)
    0.88, # P(Heatstroke = No | Weather = Moderate, WearingHat = No)
    
    0.01, # P(Heatstroke = Yes | Weather = Cold, WearingHat = Yes)
    0.99, # P(Heatstroke = No | Weather = Cold, WearingHat = Yes)
    
    0.01, # P(Heatstroke = Yes | Weather = Cold, WearingHat = No)
    0.99, # P(Heatstroke = No | Weather = Cold, WearingHat = No)
]
# -----------------

# ------ Arcs ------
net.add_arc('Weather', 'WearingHat')

net.add_arc('Weather', 'Heatstroke')
net.add_arc('WearingHat', 'Heatstroke')
# ------------------

# ------ Wiring up the node with the marginal probabilities ------
net.set_node_definition('Weather', weather_prob_dist)
net.set_node_definition('WearingHat', wearing_hat_CPT)
net.set_node_definition('Heatstroke', heatstroke_CPT)
# ----------------------------------------------------------------

net.write_file(f"{SAVEDIR}/simple_weather_model.xdsl")

# ------ Evidence ------
print("Setting Heatstroke=No.")
change_evidence_and_update(net, "Heatstroke", "Yes")

print("Setting WearHat=Yes.")
change_evidence_and_update(net, "WearingHat", "No")
# ----------------------

# ------ Posterior ------
print("Posterior: ")
print_all_posteriors(net)
# -----------------------


print(get_node_posteriors(net, "Weather"))
print(check_if_node_is_evidence(net, "Weather"))


