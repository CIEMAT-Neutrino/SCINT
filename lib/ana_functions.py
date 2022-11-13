import numpy as np
import copy
import sys

from .io_functions import load_npy,load_analysis_npy,load_average_npy
from itertools import product

def insert_variable(my_runs,VAR,KEY):
    """Insert values for each type of signal"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch][KEY] = VAR[ch]

def compute_peak_variables(my_runs,range1=0,range2=0,PATH="../data/raw/"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Peak_amp" ] =np.max    (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)
            my_runs[run][ch]["Peak_time"] =np.argmax (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)

def compute_pedestal_variables(my_runs,PATH="../data/raw/"):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            ped_lim = my_runs[run][ch]["Peak_time"]-100
            my_runs[run][ch]["Ped_STD"] =np.std (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_mean"]=np.mean(my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_max"] =np.max (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_min"] =np.min (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)

def compute_ana_wvfs(my_runs,PATH="../data/raw/"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Ana_ADC"] = my_runs[run][ch]["P_channel"]*((my_runs[run][ch]["ADC"].T-ana_runs[run][ch]["Ped_mean"]).T)

def find_baseline_cuts(RAW):
    MAX = np.argmax(RAW)
    i_idx = 0
    f_idx = 0
    
    for j in range(len(RAW[MAX:])):
        if RAW[MAX+j] < 0:
            f_idx = MAX+j
            break
    for j in range(len(RAW[:MAX])):
        if RAW[MAX-j] < 0:
            i_idx = MAX-j+1
            break
    return i_idx,f_idx

def integrate(my_runs,TYPE,PATH="../data/raw/"):  
    AVE_RUNS = load_average_npy(my_runs["N_runs"],my_runs["N_channels"])
    
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        AVE = AVE_RUNS[run][ch]["AvWvf"]
        i_idx,f_idx = find_baseline_cuts(AVE)
        aux = dict()
        for i in range(len(my_runs[run][ch]["ADC"])):
            RAW = my_runs[run][ch]["P_channel"]*(my_runs[run][ch]["ADC"][i]-my_runs[run][ch]["Ped_mean"][i])
            if TYPE == "BASELINE_INT_LIMITS": 
                INT_I,INT_F = find_baseline_cuts(RAW)
            elif TYPE == "AVE_INT_LIMITS":
                INT_I,INT_F = i_idx,f_idx
            else: 
                print("INTEGRATION TYPE IS NOT DEFINED")
                sys.exit()
            
            aux[i] = np.trapz(RAW[INT_I:INT_F],x=4e-9*np.arange(len(RAW[INT_I:INT_F])))
        
        my_runs[run][ch][TYPE] = aux
    return my_runs