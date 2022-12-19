import numpy as np
import copy
import sys

# from .io_functions import load_npy
from .io_functions import check_key, print_keys

import matplotlib.pyplot as plt
from scipy import stats as st
from itertools import product

def insert_variable(my_runs, var, key, debug = False):
    """Insert values for each type of signal"""
    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        i = np.where(np.array(my_runs["NRun"]).astype(int) == run)[0][0]
        j = np.where(np.array(my_runs["NChannel"]).astype(int) == ch)[0][0]

        try:
            my_runs[run][ch][key] = var[j]
        except: 
            KeyError
            if debug: print("Inserting value...")

def compute_peak_variables(my_runs, range1 = 0, range2 = 0, key = "ADC", debug = False):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            my_runs[run][ch]["PeakAmp" ] = np.max    (my_runs[run][ch][key][:,:]*my_runs[run][ch]["PChannel"],axis=1)
            my_runs[run][ch]["PeakTime"] = np.argmax (my_runs[run][ch][key][:,:]*my_runs[run][ch]["PChannel"],axis=1)
            print("Peak variables have been computed for run %i ch %i"%(run,ch))
        except: 
            KeyError
            if debug: print("*EXCEPTION: for ",run,ch,key," peak variables could not be computed")

def compute_pedestal_variables(my_runs, key = "ADC", debug = False):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""
    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        try:
            buffer = 200
            ped_lim = st.mode(my_runs[run][ch]["PeakTime"])[0][0]-buffer
            if ped_lim < 0: ped_lim = 50
            my_runs[run][ch]["PedSTD"]  = np.std (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["PedMean"] = np.mean(my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["PedMax"]  = np.max (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["PedMin"]  = np.min (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch]["PedLim"]  = ped_lim
            print("Pedestal variables have been computed for run %i ch %i"%(run,ch))
        except: 
            KeyError
            if debug: print("*EXCEPTION: for ",run,ch,key," pedestal variables could not be computed")

def compute_ana_wvfs(my_runs, debug = False):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        try:
            my_runs[run][ch]["AnaADC"] = my_runs[run][ch]["PChannel"]*((my_runs[run][ch]["ADC"].T-my_runs[run][ch]["PedMean"]).T)
            print("Analysis wvfs have been computed for run %i ch %i"%(run,ch))
            if debug: print_keys(my_runs)
        except: 
            KeyError
            if debug: print("*EXCEPTION: for ",run,ch," ana wvfs could not be computed")
        if debug:
            plt.plot(4e-9*np.arange(len(my_runs[run][ch]["AnaADC"][0])),my_runs[run][ch]["AnaADC"][0])
            plt.show()