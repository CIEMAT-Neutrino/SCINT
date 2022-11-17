import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,save_proccesed_variables
from lib.fit_functions import fit_wvfs

# import matplotlib.pyplot as plt
# import numpy as np

N_runs     = [12,13,14]     
N_channels = [0,1,6]       

RUNS = load_npy(N_runs,N_channels,"Analysis_","../data/ana/")

# print(RUNS[26][1]["Sampling"])
FIT_RANGE = [80,600] # Fit range in units of array length defined left and right from the max (peak of the wvf)

OPT = {
    "SHOW":True,
    "LOGY":True,
    "AVE":"Ana_ADC",
    # "AVE":"Deconvolution"
    } 

fit_wvfs(RUNS,"SCINT",FIT_RANGE,OPT)

save_proccesed_variables(RUNS,"Fit_","../data/fit/")
