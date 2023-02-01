import sys
sys.path.insert(0, '../')
import numpy as np
import matplotlib.pyplot as plt
from lib.io_functions import load_npy

run = 22
ch  = 6
key = "DecADC"

my_runs = load_npy([run],[ch],"Deconvolution_","../data/dec/")

# my_runs.keys()
plt.ion()
next_plot = False
for i in range(len(my_runs[run][ch][key])):
    plt.plot(my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch][key][i])),my_runs[run][ch][key][i],label="#PE %.2f"%np.sum(my_runs[run][ch][key][i]))
    plt.xlabel("Time in [s]")
    plt.ylabel("Amp in a.u.")
    plt.semilogy()
    plt.legend()
    while not plt.waitforbuttonpress(-1): pass
    plt.clf()

plt.ioff()