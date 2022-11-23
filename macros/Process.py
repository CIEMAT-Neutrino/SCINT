import sys
sys.path.insert(0, '../')

import numpy as np
from lib.io_functions  import read_input_file,load_npy,delete_keys,save_proccesed_variables
from lib.ana_functions import compute_pedestal_variables,compute_peak_variables,compute_ana_wvfs,insert_variable
from itertools import product

input_file = input("Please select input File: ")
info = read_input_file(input_file)

RUNS = []; CH = []
RUNS = np.append(RUNS,info["CALIB_RUNS"])
RUNS = np.append(RUNS,info["LIGHT_RUNS"])
RUNS = np.append(RUNS,info["ALPHA_RUNS"])

CH = np.append(CH,info["CHAN_STNRD"])

""" To-Do: Avoid using loop in this macro. Maybe "ADC" type dict can be loaded in lazy mode """

# PROCESS WAVEFORMS (Run in loop to avoid memory issues)

for run, ch in product(RUNS.astype(int),CH.astype(int)):
    
    my_runs = load_npy([run],[ch])
    compute_ana_wvfs(my_runs,debug=False)

    delete_keys(my_runs,['Peak_amp', 'Peak_time', 'Ped_STD', 'Ped_mean', 'Ped_max', 'Ped_min', 'Ped_lim','P_channel']) # Delete raw peak and pedestal variables
    insert_variable(my_runs,[1,1,1,1],"P_channel") # Change polarity!
    
    compute_peak_variables(my_runs,key="Ana_ADC")
    compute_pedestal_variables(my_runs,key="Ana_ADC",debug=True)
    
    delete_keys(my_runs,["ADC"])
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")