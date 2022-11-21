import sys
sys.path.insert(0, '../')
import numpy as np
import matplotlib.pyplot as plt
from lib.io_functions import load_npy

run = 22
ch  = 6
key = "Dec_Ana_ADC"

RUNS = load_npy([run],[ch],"Deconvolution_","../data/dec/")

# RUNS.keys()
plt.ion()
next_plot = False
for i in range(len(RUNS[run][ch][key])):
    plt.plot(RUNS[run][ch]["Sampling"]*np.arange(len(RUNS[run][ch][key][i])),RUNS[run][ch][key][i],label="#PE %.2f"%np.sum(RUNS[run][ch][key][i]))
    plt.xlabel("Time in [s]")
    plt.ylabel("Amp in a.u.")
    plt.semilogy()
    plt.legend()
    while not plt.waitforbuttonpress(-1): pass
    plt.clf()

plt.ioff()