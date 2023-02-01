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

def generate_cut_array(my_runs):
    """
    This function generates an array of bool = True with length = NEvts. If cuts are applied and then you run this function, it resets the cuts.
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):    
        for key in my_runs[run][ch].keys():
            if key.find("ADC") > 0:
                ADC_key = key
        my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][ADC_key]),dtype=bool)

def compute_peak_variables(my_runs, key = "ADC", label = "", debug = False):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            my_runs[run][ch][label+"PeakAmp" ] = np.max    (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
            my_runs[run][ch][label+"PeakTime"] = np.argmax (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
            print("Peak variables have been computed for run %i ch %i"%(run,ch))
        except: 
            KeyError
            if debug: print("*EXCEPTION: for ",run,ch,key," peak variables could not be computed")

def compute_pedestal_variables(my_runs, key = "ADC", label = "", buffer = 200, debug = False):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            ped_lim = st.mode(my_runs[run][ch][label+"PeakTime"])[0][0]-buffer
            if ped_lim < 0: ped_lim = 50
            my_runs[run][ch][label+"PedSTD"]  = np.std (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMean"] = np.mean(my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMax"]  = np.max (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMin"]  = np.min (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedLim"]  = ped_lim
            print("Pedestal variables have been computed for run %i ch %i"%(run,ch))
        except: 
            KeyError
            if debug: print("*EXCEPTION: for ",run,ch,key," pedestal variables could not be computed")

def compute_ana_wvfs(my_runs, debug = False):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):

        my_runs[run][ch]["ADC"] = my_runs[run][ch]["RawPChannel"]*((my_runs[run][ch]["RawADC"].T-my_runs[run][ch]["RawPedMean"]).T)
        print("Analysis wvfs have been computed for run %i ch %i"%(run,ch))
        if debug: print_keys(my_runs)

        del my_runs[run][ch]["RawADC"] # After ADC is computed, delete RawADC from memory

def get_units(my_runs, debug = False):
    for run, ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        keys = my_runs[run][ch].keys()
        aux_dic = {}
        for key in keys:
            if "Amp" in key or "Ped" in key or "ADC" in key:
                aux_dic[key] = "ADC"
            elif "Time" in key or "Sampling" in key:
                aux_dic[key] = "s"
            elif "Charge" in key:
                aux_dic[key] = "pC"
            else:
                aux_dic[key] = "a.u."
        my_runs[run][ch]["Units"] = aux_dic