import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,save_proccesed_variables
from lib.fit_functions import fit_wvfs

# import matplotlib.pyplot as plt
# import numpy as np

N_runs     = [25,26,27]     
N_channels = [4]       

RUNS = load_npy(N_runs,N_channels,"Average_","../data/ave/")
# RUNS = load_npy(N_runs,N_channels,"Deconvolution_","../data/dec/")

THRLD = 1e-6
FIT_RANGE = [80,1000] # Fit range in units of array length defined left and right from the max (peak of the wvf)

OPT = {
    "SHOW":True,
    "LOGY":True,
    "NORM":True
    }

KEY = ["AvWvf"]

fit_wvfs(RUNS,"SCINT",THRLD,FIT_RANGE,KEY,OPT)

save_proccesed_variables(RUNS,"Fit_","../data/fit/")