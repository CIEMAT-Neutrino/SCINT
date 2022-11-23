import sys
sys.path.insert(0, '../')

import numpy as np
from lib.io_functions  import load_npy,delete_keys,save_proccesed_variables
from lib.ana_functions import compute_pedestal_variables,compute_peak_variables,compute_ana_wvfs,insert_variable
from itertools import product

# Arrays used in load_run
RUNS=[9,10,11,25,26,27]
RUNS_CALIB=[1,2,3]

CH=[0,1,4,6]
CH_CALIB=[0,1,6]

# Missing variables to be inserted
POLARITY       = [-1,-1,-1,-1]   #polarity
SAMPLING       = [4e-9,4e-9,4e-9,4e-9]
LABELS         = ["SiPM","SiPM","PMT","SC"]
LABELS_CALIB   = ["SiPM","SiPM","SC"]

# # OTHER RUNS
# # PRE-PROCESS RAW
# for run, ch in product(RUNS,CH):
#     # Start load_run 
#     my_runs = load_npy([run], [ch])
    
#     insert_variable(my_runs,POLARITY,"P_channel")
#     insert_variable(my_runs,SAMPLING,"Sampling")
#     insert_variable(my_runs,LABELS,"Label")
    
#     compute_peak_variables(my_runs)
#     compute_pedestal_variables(my_runs)
#     print(my_runs.keys())
    
#     save_proccesed_variables(my_runs,"","../data/raw/")

# SECOND PROCESS - PROCESSED WAVEFORMS
for run, ch in product(RUNS,CH):
    my_runs = load_npy([run], [ch])
    
    compute_ana_wvfs(my_runs) 
    # Run appropiate ana_functions    
    compute_peak_variables(my_runs,"Ana_ADC")
    insert_variable(my_runs,[1,1,1,1],"P_channel") # Change polarity!
    compute_pedestal_variables(my_runs,"Ana_ADC")
    
    delete_keys(my_runs,["ADC"])
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")

# # CALIBRATION RUNS
# # PRE-PROCESS RAW
# for run, ch in product(RUNS_CALIB,CH_CALIB):
#     # Start load_run 
#     my_runs = load_npy([run], [ch])

#     insert_variable(my_runs,POLARITY,"P_channel")
#     insert_variable(my_runs,SAMPLING,"Sampling")
#     insert_variable(my_runs,LABELS_CALIB,"Label")
    
#     compute_peak_variables(my_runs)
#     compute_pedestal_variables(my_runs)
#     print(my_runs.keys())
    
#     save_proccesed_variables(my_runs,"","../data/raw/")

# SECOND PROCESS - PROCESSED WAVEFORMS
for run, ch in product(RUNS_CALIB,CH_CALIB):
    my_runs = load_npy([run], [ch])
    
    compute_ana_wvfs(my_runs)
    # delete_keys(my_runs,["ADC","Peak_amp","Peak_time","Ped_lim"])
    # Run appropiate ana_functions
    compute_peak_variables(my_runs,"Ana_ADC")
    insert_variable(my_runs,[1,1,1,1],"P_channel") # Change polarity!
    compute_pedestal_variables(my_runs,"Ana_ADC")
    
    delete_keys(my_runs,["ADC"])
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")

