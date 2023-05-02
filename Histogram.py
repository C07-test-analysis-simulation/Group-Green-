import numpy as np
from FindLoss import table, tracks_total_duration
import matplotlib.pyplot as plt

durationlist = table[:, 2]
width = 20
bins = range(int(np.min(durationlist)), int(np.max(durationlist))+width+1, width)

plt.hist(durationlist, bins = 'auto')
plt.suptitle("Nominal receiver", fontweight='bold')
plt.title(f"Total duration of losses: {np.sum(table[:, 2], axis=0)} s ({round(np.sum(table[:, 2], axis=0)/tracks_total_duration * 100, 3)} %); Median: {np.median(table[:, 2], axis=0)} s", fontsize=10)
plt.ylabel("Number [-]")
plt.xlabel("Duration [s]")
plt.yscale('log')
plt.show()

print("finsihed")