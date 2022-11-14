import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy
from lib.fit_functions import fit_wvfs

# import matplotlib.pyplot as plt
# import numpy as np

N_runs     = [2]     
N_channels = [0,1]       

RUNS = load_npy(N_runs,N_channels,"Average_","../data/ave/")

FIT_RANGE = [80,750] # Fit range in units of array length defined left and right from the max (peak of the wvf)

OPT = {
    "SHOW":True,
    "LOGY":False,
    "AVE":"SPE_AvWvf",
    # "AVE":"Deconvolution"
    } 

fit_wvfs(RUNS,"SiPM",FIT_RANGE,OPT)

save_proccesed_variables(RUNS,"Fit_","../data/fit/")
