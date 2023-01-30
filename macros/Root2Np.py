# RUN ONLY IF DATA HAS NOT YET BEEN CONVERTED TO NPY

import sys
sys.path.insert(0, '../')

import numpy as np
from itertools import product
from lib.io_functions import read_input_file,root2npy,load_npy,save_proccesed_variables
from lib.ana_functions import compute_peak_variables,compute_pedestal_variables

if sys.argv[1]: input_file = sys.argv[1]
else          : input_file = input("Please select input File: ")

info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])
# runs = np.append(runs,info["MUONS_RUNS"])

channels = np.append(channels,info["CHAN_STNRD"])

root2npy(runs.astype(int),channels.astype(int),info=info)

""" !!! To Do: section below coud be included inside root2npy function. !!! """ 

# PRE-PROCESS RAW 
for run, ch in product(runs.astype(int),channels.astype(int)):
    # Start to load_runs 
    my_runs = load_npy([run],[ch])
    
    compute_peak_variables(my_runs)
    compute_pedestal_variables(my_runs)
    print(my_runs.keys())
    save_proccesed_variables(my_runs,"","../data/raw/")