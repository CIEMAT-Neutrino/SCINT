import sys
sys.path.insert(0, '../')

import numpy as np
from itertools import product
from lib.io_functions import read_input_file,root2npy,load_npy,save_proccesed_variables
from lib.ana_functions import compute_peak_variables,compute_pedestal_variables

input_file = input("Please select input File: ")
info = read_input_file(input_file)

RUNS = []; CH = []
RUNS = np.append(RUNS,info["CALIB_RUNS"])
RUNS = np.append(RUNS,info["LIGHT_RUNS"])
RUNS = np.append(RUNS,info["ALPHA_RUNS"])

CH = np.append(CH,info["CHAN_STNRD"])

root2npy(RUNS.astype(int),CH.astype(int),info=info)

# PRE-PROCESS RAW
for run, ch in product(RUNS.astype(int),CH.astype(int)):
    # Start to load_runs 
    my_runs = load_npy([run],[ch])
    
    compute_peak_variables(my_runs)
    compute_pedestal_variables(my_runs)
    print(my_runs.keys())
    
    save_proccesed_variables(my_runs,"","../data/raw/")