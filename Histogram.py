import numpy as np
from FindLossV2 import table, tracks_total_duration
import matplotlib.pyplot as plt

'''
General notes & remarks:
- THIS IS FINAL VERSION (04.05)
- THIS HAS BEEN CLEANED
'''

durationlist = table[:, 2] #We get the durations of losses from the 'FindLoss' file.
width = 20 
bins = range(int(np.min(durationlist)), int(np.max(durationlist))+width+1, width) #We set the binwidths of the histogram.

#We plot the histogram including a title, subtitle, axis-labels. A logarithmic scale is chosen.
plt.hist(durationlist, bins = 'auto')
plt.suptitle("Redundant receiver", fontweight='bold')
plt.title(f"Total duration of losses: {np.sum(table[:, 2], axis=0)} s ({round(np.sum(table[:, 2], axis=0)/tracks_total_duration * 100, 3)} %); Median: {np.median(table[:, 2], axis=0)} s", fontsize=10)
plt.ylabel("Number [-]")
plt.xlabel("Duration [s]")
plt.yscale('log')
plt.show()