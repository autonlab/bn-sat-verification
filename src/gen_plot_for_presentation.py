import numpy as np
import pysmile
import pysmile_license
from pysmile_utils import *
import matplotlib.pyplot as plt

N = 500
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
                [f'{i}yr' for i in range(N)], 
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
    0.5, 0.5
]
# ------------------------------------

# ------ CPT ------
# workexperiecnce_hat_CPT = [
# # #   1yr, 2yr, 3yr, 4yr
# #     0.1, 0.2, 0.5, 0.8, # Yes
# #     0.9, 0.8, 0.5, 0.2, # No
# ]

# pos = np.array([i**0.1 if i < N//4 else (i - 50)**0.1 for i in range(N)])
pos = np.array([i**2 if i < N - N//3 else (i - 50)**2 for i in range(N)])
# pos = np.array([i**2 for i in range(N)])
pos = pos / pos.max()
neg = np.array([1-pos[i] for i in range(N)])
workexperiecnce_hat_CPT = pos.tolist() + neg.tolist()
print(len(workexperiecnce_hat_CPT))




gpa_CPT = [
#   True, False
    0.9, 0.05, # True
    0.1, 0.95, # False
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


posteriors_while_changing_workexperience = []

for outcome in net.get_outcome_ids("WorkExperience"):
    # ------ Evidence ------
    # print("Setting GPA=False.")
    # change_evidence_and_update(net, "GPA", "False")
    print("Setting WorkExperience={}".format(outcome))
    change_evidence_and_update(net, "WorkExperience", outcome)
    # ----------------------

    # ------ Posterior ------
    post_true = get_node_posteriors(net, "Admit")[0][1]
    posteriors_while_changing_workexperience.append(post_true)
    # -----------------------

print(posteriors_while_changing_workexperience)


plt.plot(posteriors_while_changing_workexperience)
plt.title("Probability of overheating")
plt.xlabel("Temperature (°C)")
plt.ylabel("Posterior Probability\nP(Overheat = True | Temperature))")

# Set own xticks -> scale it to 0-70
# Show only every 10th xtick    
plt.xticks(range(0, N, 50), [f'{i//5}' for i in range(N)][::50])

plt.tight_layout()
plt.show()