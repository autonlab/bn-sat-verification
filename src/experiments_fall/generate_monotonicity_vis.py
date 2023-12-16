import matplotlib.pyplot as plt
import numpy as np
import os


#plot 1 data
x1 = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
y1 = np.array([0, 0, 0, 1, 1, 0, 0, 0, 0, 0])

# plot 2 data
x2 = x1
y2 = 1 - y1

# plot 3 data
x3 = x2
y3 = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])

# plot 4 data monotonically decreasing
x4 = x3
y4 = 1 - y3

#plot 5 data monotonically stable at 1 
x5 = x3
y5 = np.ones(len(y3))

#plot 6 data monotonically stable at 0
x6 = x3
y6 = np.zeros(len(y3))





# Plot them adjacently
fig, ax = plt.subplots(2, 3, figsize=(12, 6))

ax=ax.flatten()

ax[0].plot(x1, y1, 'k')
ax[0].set_title('Low-High-Low')
# ax[0].set_xlabel('X')
ax[0].set_ylabel('Y', rotation=90)
ax[0].set_yticks([0, 1])
ax[0].set_ylim([-0.1, 1.1])
ax[0].set_xticks([])

ax[1].plot(x2, y2, 'k')
ax[1].set_title('High-Low-High')
# ax[1].set_xlabel('X')
# ax[1].set_ylabel('Y', rotation=90)
ax[1].set_yticks([0, 1])
ax[1].set_ylim([-0.1, 1.1])
ax[1].set_xticks([])

ax[2].plot(x3, y3, 'k')
ax[2].set_title('Monotonically Increasing')
# ax[2].set_xlabel('X')
# ax[2].set_ylabel('Y', rotation=90)
ax[2].set_yticks([0, 1])
ax[2].set_ylim([-0.1, 1.1])
ax[2].set_xticks([])

ax[3].plot(x4, y4, 'k')
ax[3].set_title('Monotonically Decreasing')
ax[3].set_xlabel('X')
ax[3].set_ylabel('Y', rotation=90)
ax[3].set_yticks([0, 1])
ax[3].set_ylim([-0.1, 1.1])

ax[4].plot(x5, y5, 'k')
ax[4].set_title('Monotonically Stable at 1')
ax[4].set_xlabel('X')
ax[4].set_yticks([0, 1])
# ax[4].set_xticks([0, 1, 2, 3])
ax[4].set_ylim([-0.1, 1.1])

ax[5].plot(x6, y6, 'k')
ax[5].set_title('Monotonically Stable at 0')
ax[5].set_xlabel('X')
ax[5].set_yticks([0, 1])
ax[5].set_ylim([-0.1, 1.1])

# set title font size
for a in ax:
    a.title.set_fontsize(14)

plt.tight_layout()


# Save the figure in current directory. In high resolution.
path = os.path.join(os.path.dirname(__file__), 'monotonicity_vis')

# Save as png
plt.savefig(path + '.png', dpi=300)

# Save as eps. No psfrags.
plt.savefig(path + '.eps', dpi=300)



plt.show()
