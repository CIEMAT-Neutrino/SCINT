import numpy as np
import copy
import sys

# from .io_functions import load_npy
from scipy import stats as st
from itertools import product

def insert_variable(my_runs,var,key):
    """Insert values for each type of signal"""
    for run,ch in product(my_runs["N_runs"].astype(int),my_runs["N_channels"].astype(int)):
        i = np.where(RUNS==run)[0][0]
        j = np.where(CHANNELS==ch)[0][0]

        my_runs[run][ch][key] = var[j]

def compute_peak_variables(my_runs,range1=0,range2=0,key="ADC"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run,ch in product(my_runs["N_runs"].astype(int),my_runs["N_channels"].astype(int)):
        my_runs[run][ch]["Peak_amp" ] = np.max    (my_runs[run][ch][key][:,:]*my_runs[run][ch]["P_channel"],axis=1)
        my_runs[run][ch]["Peak_time"] = np.argmax (my_runs[run][ch][key][:,:]*my_runs[run][ch]["P_channel"],axis=1)
        print("Peak variables have been computed for run %i ch %i"%(run,ch))

def compute_pedestal_variables(my_runs,key="ADC"):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
        
            buffer = 50
            ped_lim = st.mode(my_runs[run][ch]["Peak_time"])[0][0]-buffer
            # print(my_runs[run][ch]["Peak_time"])
            # print(ped_lim)
            my_runs[run][ch]["Ped_STD"]  = np.std (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_mean"] = np.mean(my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_max"]  = np.max (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["Ped_min"]  = np.min (my_runs[run][ch][key][:,:ped_lim],axis=1)

            my_runs[run][ch]["Ped_lim"]  = ped_lim
            print("Pedestal variables have been computed for run %i ch %i"%(run,ch))

def compute_ana_wvfs(my_runs):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        my_runs[run][ch]["Ana_ADC"] = my_runs[run][ch]["P_channel"]*((my_runs[run][ch]["ADC"].T-my_runs[run][ch]["Ped_mean"]).T)
        print("Analysis wvfs have been computed for run %i ch %i"%(run,ch))