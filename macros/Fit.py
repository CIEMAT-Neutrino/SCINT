import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy,load_average_npy,load_fit_npy,load_deconvolution_npy
from lib.fit_functions import sipm_fit,scint_fit,sc_fit,fit_wvfs
import matplotlib.pyplot as plt
import numpy as np

N_runs     =[26]     
N_channels =[6]       

# RUNS = load_npy(N_runs, N_channels)
# AVE_RUNS = load_average_npy(N_runs, N_channels)
DEC_RUNS = load_deconvolution_npy(N_runs, N_channels)

FIT_RANGE = [80,300] # Fit range in units of array length defined left and right from the max (peak of the wvf)

OPT = {
    "SHOW":True,
    "LOGY":True,
    "AVE":"Deconvolution"
    } 

fit_wvfs(DEC_RUNS,"SCINT",FIT_RANGE,OPT)