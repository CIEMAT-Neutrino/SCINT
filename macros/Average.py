import sys
sys.path.insert(0, '../')

from lib.io_functions import read_input_file,load_npy,delete_keys,save_proccesed_variables
from lib.wvf_functions import average_wvfs,integrate_wvfs

import numpy as np
from itertools import product

input_file = input("Please select input File: ")
info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])

channels = np.append(channels,info["CHAN_STNRD"])      

del_keys = ["AnaADC"]

""" To-Do: Simple average has already been computed in Process.py here a more refined Average should be computed: e.g. SPE for CALIB RUNS... """

# PROCESS WAVEFORMS (Run in loop to avoid memory issues)
for run, ch in product(runs.astype(int),channels.astype(int)):
    # Start load_run 
    my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")

    integrate_wvfs(my_runs,["Range"],"AveWvf",["DAQ", 250],[0,100])
    print(my_runs[run][ch]["AnaADC"])
    delete_keys(my_runs,del_keys)
    save_proccesed_variables(my_runs,"Average_","../data/ave/")