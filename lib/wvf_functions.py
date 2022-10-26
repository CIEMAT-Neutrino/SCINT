# import copy
import numpy as np
from .io_functions import load_analysis_npy, load_npy
from itertools import product

def average_wvfs(my_runs,PATH="../data/ave/"):
    
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

def integrate(my_runs,PATH="../data/ana/"):
    
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("EVENTS HAVE NOT BEEN PROCESSED! Please run Process.py")
        return 0

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        for i in range(len(my_runs[run][ch]["ADC"])):
            RAW = ana_runs[run][ch]["P_channel"]*(my_runs[run][ch]["ADC"][i]-ana_runs[run][ch]["Ped_mean"][i])
            MAX = np.argmax(RAW)
            INT_I = 0
            INT_F = 0
            
            for j in range(len(RAW[MAX:])):
                if RAW[MAX+j] < 0:
                    INT_F = MAX+j
                    break
            for j in range(len(RAW[:MAX])):
                if RAW[MAX-j] < 0:
                    INT_I = MAX-j+1
                    break
            print(RAW[INT_I:INT_F])
            my_runs[run][ch]["Int"][i] = np.trapz(RAW[INT_I:INT_F],x=4e-9*np.arange(len(RAW[INT_I:INT_F])))