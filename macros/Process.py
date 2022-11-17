import sys
sys.path.insert(0, '../')

import numpy as np
from lib.io_functions  import load_npy,delete_keys,save_proccesed_variables
from lib.ana_functions import compute_pedestal_variables,compute_peak_variables,compute_ana_wvfs,insert_variable
from itertools import product

# Arrays used in load_run
N_runs           = [10,22,26]     
N_runs_calib     = [2]     
N_channels       = [0,1,4,6]       
N_channels_calib = [0,1,6]

# Missing variables to be inserted
POLARITY = [-1,-1,-1,-1]   #polarity
SAMPLING = [4e-9,4e-9,4e-9,4e-9]
LABELS   = ["SiPM","SiPM","PMT","SC"]
LABELS_CALIB   = ["SiPM","SiPM","SC"]

# OTHER RUNS
# PRE-PROCESS RAW
for run, ch in product(N_runs,N_channels):
    # Start load_run 
    RUNS       = load_npy([run], [ch])
    insert_variable(RUNS,POLARITY,"P_channel")
    insert_variable(RUNS,SAMPLING,"Sampling")
    insert_variable(RUNS,LABELS,"Label")
    compute_peak_variables(RUNS)
    compute_pedestal_variables(RUNS)
    print(RUNS.keys())
    save_proccesed_variables(RUNS,"","../data/raw/")
# SECOND PROCESS - PROCESSED WAVEFORMS
for run, ch in product(N_runs,N_channels):
    RUNS       = load_npy([run], [ch])
    compute_ana_wvfs(RUNS) 
    # Run appropiate ana_functions
    insert_variable(RUNS,-1*np.array(POLARITY),"P_channel") # Change polarity!
    insert_variable(RUNS,SAMPLING,"Sampling")
    insert_variable(RUNS,LABELS,"Label")
    compute_peak_variables(RUNS,"Ana_ADC")
    compute_pedestal_variables(RUNS,"Ana_ADC")
    delete_keys(RUNS,["ADC"])
    save_proccesed_variables(RUNS,"Analysis_","../data/ana/")


# CALIBRATION RUNS
# PRE-PROCESS RAW
for run, ch in product(N_runs_calib,N_channels_calib):
    # Start load_run 
    RUNS       = load_npy([run], [ch])
    insert_variable(RUNS,POLARITY,"P_channel")
    insert_variable(RUNS,SAMPLING,"Sampling")
    insert_variable(RUNS,LABELS_CALIB,"Label")
    compute_peak_variables(RUNS)
    compute_pedestal_variables(RUNS)
    print(RUNS.keys())
    save_proccesed_variables(RUNS,"","../data/raw/")
# SECOND PROCESS - PROCESSED WAVEFORMS
for run, ch in product(N_runs_calib,N_channels_calib):
    RUNS       = load_npy([run], [ch])
    compute_ana_wvfs(RUNS) 
    # Run appropiate ana_functions
    insert_variable(RUNS,-1*np.array(POLARITY),"P_channel") # Change polarity!
    insert_variable(RUNS,SAMPLING,"Sampling")
    insert_variable(RUNS,LABELS_CALIB,"Label")
    compute_peak_variables(RUNS,"Ana_ADC")
    compute_pedestal_variables(RUNS,"Ana_ADC")
    delete_keys(RUNS,["ADC"])
    save_proccesed_variables(RUNS,"Analysis_","../data/ana/")