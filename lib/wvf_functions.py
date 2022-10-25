# import copy
import numpy as np
from .my_functions import load_analysis_npy, load_npy
from itertools import product

def average_wvf(my_runs,PATH="../data/ave/"):
    
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("EVENTS HAVE NOT BEEN PROCESSED! Please run Process.py")
        return 0

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        # print(run,ch)
        my_runs[run][ch]["ADC"] = ana_runs[run][ch]["P_channel"]*np.mean((my_runs[run][ch]["ADC"].T-ana_runs[run][ch]["Ped_mean"]).T,axis=0)
        aux_path=PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
        np.save(aux_path,my_runs[run][ch])
        print("Saved data in:" , aux_path)