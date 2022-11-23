import sys
sys.path.insert(0, '../')

import numpy as np
from lib.io_functions  import load_npy,print_keys,delete_keys,save_proccesed_variables
from lib.ana_functions import compute_pedestal_variables,compute_peak_variables,compute_ana_wvfs,insert_variable
from itertools import product

# Arrays used in load_run
RUNS    = [1,5]
# CH=[0,1,4,6] # SiPM1, SiPM2, PMT, XA
CH      = [0]

# Missing variables to be inserted
POLARITY       = [-1,-1,-1,-1]   #Polarity
SAMPLING       = [4e-9,4e-9,4e-9,4e-9]
LABELS         = ["SiPM","SiPM","PMT","SC"]
LABELS_CALIB   = ["SiPM","SiPM","SC"]

OPT  = {
    "PRINT_KEYS":       False
    }

# # OTHER RUNS
# # PRE-PROCESS RAW
# for run, ch in product(RUNS,CH):
#     # Start load_run 
# my_runs = load_npy(RUNS, CH) #Funciona aunque no tengamos este bucle exterior y demos un array directamente.
    # my_runs = load_npy([run], [ch])
#     my_runs = load_npy([run], [ch])
#     insert_variable(my_runs,POLARITY,"P_channel")
#     insert_variable(my_runs,SAMPLING,"Sampling")
#     insert_variable(my_runs,LABELS,"Label")
    
#     compute_peak_variables(my_runs)
#     compute_pedestal_variables(my_runs)
    
#     print(my_runs.keys())
    # print_keys(my_runs)
    
#     save_proccesed_variables(my_runs,"","../data/raw/")

# SECOND PROCESS - PROCESSED WAVEFORMS
for run, ch in product(RUNS,CH):
    my_runs = load_npy([run], [ch])
    
    compute_ana_wvfs(my_runs,OPT["PRINT_KEYS"]) 
    # Run appropiate ana_functions    
    compute_peak_variables(my_runs,"Ana_ADC")
    insert_variable(my_runs,[1,1,1,1],"P_channel") # Change polarity!
    compute_pedestal_variables(my_runs,"Ana_ADC")
    
    delete_keys(my_runs,["ADC"])
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")

# CALIBRATION RUNS
# PRE-PROCESS RAW
for run, ch in product(RUNS_CALIB,CH_CALIB):
    # Start load_run 
    my_runs = load_npy([run], [ch])

    insert_variable(my_runs,POLARITY,"P_channel")
    insert_variable(my_runs,SAMPLING,"Sampling")
    insert_variable(my_runs,LABELS_CALIB,"Label")
    
    compute_peak_variables(my_runs)
    compute_pedestal_variables(my_runs)
    print(my_runs.keys())
    
    save_proccesed_variables(my_runs,"","../data/raw/")

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