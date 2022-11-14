import numpy as np
import copy
import sys

# from .io_functions import load_npy
from itertools import product

def insert_variable(my_runs,VAR,KEY):
    """Insert values for each type of signal"""
    for run in my_runs["N_runs"]:
        index = 0
        for ch in my_runs["N_channels"]:
            my_runs[run][ch][KEY] = VAR[index]
            index = index + 1

def compute_peak_variables(my_runs,range1=0,range2=0,PATH="../data/raw/"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Peak_amp" ] = np.max    (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)
            my_runs[run][ch]["Peak_time"] = np.argmax (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)
            print("Peak variables have been computed for run %i ch %i"%(run,ch))

def compute_pedestal_variables(my_runs,PATH="../data/raw/"):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            buffer = 100
            ped_lim = int(np.bincount(my_runs[run][ch]["Peak_time"]).argmax()-buffer)
            my_runs[run][ch]["Ped_STD"]  = np.std (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_mean"] = np.mean(my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_max"]  = np.max (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_min"]  = np.min (my_runs[run][ch]["ADC"][:,:ped_lim],axis=1)
            print("Pedestal variables have been computed for run %i ch %i"%(run,ch))

def compute_ana_wvfs(my_runs,PATH="../data/raw/"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Ana_ADC"] = my_runs[run][ch]["P_channel"]*((my_runs[run][ch]["ADC"].T-my_runs[run][ch]["Ped_mean"]).T)
            print("Analysis wvfs have been computed for run %i ch %i"%(run,ch))