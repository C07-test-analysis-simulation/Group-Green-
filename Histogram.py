import numpy as np
from FindLoss import table
import matplotlib.pyplot as plt

durationlist = table[:, 2]
width = 5

bins = range(int(np.min(durationlist)), int(np.max(durationlist))+width+1, width)
plt.hist(durationlist, bins = 'auto')
plt.show()
print("finsihed")