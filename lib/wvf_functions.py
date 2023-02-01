# import copy
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats as st
from .io_functions import check_key
from .cut_functions import generate_cut_array
from itertools import product

def find_baseline_cuts(raw):
    """
    It finds the cuts with the x-axis. It returns the index of both bins.
    VARIABLE:
        - raw: the .root that you want to analize.
    """

    max   = np.argmax(raw)
    i_idx = 0
    f_idx = 0
    
    for j in range(len(raw[max:])):
        if raw[max+j] < 0:
            f_idx = max+j
            break
    for j in range(len(raw[:max])):
        if raw[max-j] < 0:
            i_idx = max-j+1
            break
    return i_idx,f_idx

def find_amp_decrease(raw,thrld):
    """
    It finds bin where the amp has fallen above a certain threshold relative to the main peak. It returns the index of both bins.
    VARIABLE:
        - raw: the np array that you want to analize.
        - thrld: the relative amp that you want to analize.
    """

    max   = np.argmax(raw)
    i_idx = 0
    f_idx = 0
    
    for j in range(len(raw[max:])):
        if raw[max+j] < np.max(raw)*thrld:
            f_idx = max+j
            break
    for j in range(len(raw[:max])):
        if raw[max-j] < np.max(raw)*thrld:
            i_idx = max-j+1
            break
    return i_idx,f_idx

def average_wvfs(my_runs, centering="NONE", threshold=0, cut_label="", OPT={}):
    """
    It calculates the average waveform of a run in three different ways:
        - AveWvf: each event is added without centering
        - AveWvfPeak: 
        - AveWvfThreshold: 
    """

    for run,ch in product(my_runs["NRun"], my_runs["NChannel"]):
        try:
            if check_key(my_runs[run][ch], "MyCuts") == True:
                print("Calculating average wvf with cuts")
            else:
                generate_cut_array(my_runs)
                cut_label = ""
            
            # centering none
            if centering == "NONE":
                mean_ana_ADC = np.mean(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True],axis=0)
                my_runs[run][ch]["AveWvf"+cut_label] = [mean_ana_ADC]
            
            # centering peak
            if centering == "PEAK":
                aux_ADC = my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True]
                bin_ref_peak = st.mode(np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True],axis=1)) #using the mode peak as reference
                bin_max_peak = np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True],axis=1) 
                my_runs[run][ch]["AveWvfPeak"+cut_label] = np.roll(aux_ADC, bin_ref_peak[0] - bin_max_peak,axis=1)

            # centering thld
            if centering == "THRESHOLD":
                if threshold == 0: threshold = np.max(mean_ana_ADC)/2
                bin_ref_thld = st.mode(np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True]>threshold,axis=1)) #using the mode peak as reference
                bin_max_thld = np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True]>threshold,axis=1) 
                my_runs[run][ch]["AveWvfThreshold"+cut_label] = np.roll(aux_ADC, bin_ref_thld[0] - bin_max_thld,axis=1)

        except KeyError:
            print("Empty dictionary. No average to compute.")

def expo_average(my_run, alpha):
    """ DOC """
    v_averaged    = np.zeros(len(my_run))
    v_averaged[0] = my_run[0]
    for i in range (len(my_run) - 1):
        v_averaged[i+1] = (1-alpha) * v_averaged[i] + alpha * my_run[i+1]
    return v_averaged

def unweighted_average(my_run):
    """ DOC """
    v_averaged     = np.zeros(len(my_run))
    v_averaged[ 0] = my_run[ 0]
    v_averaged[-1] = my_run[-1]

    for i in range (len(my_run) - 2):
        v_averaged[i+1] = (my_run[i] + my_run[i+1] + my_run[i+2]) / 3
    return v_averaged

def smooth(my_run, alpha):
    """ DOC """
    my_run = expo_average(my_run, alpha)
    my_run = unweighted_average(my_run)
    return my_run

def integrate_wvfs(my_runs, types, ref, factors, ranges):
    """
    This function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    VARIABLES:
        - my_runs: run(s) we want to use
        - types: indicates the way to make the integration. Type String.
            a) ChargeAveRange: it takes the average waveform and computes the values when the average crosses the baseline
            b) ChargeRange: it integrates in the time window specified by yourself in the vairable "ranges"
        - ref: STRING for key used as integration reference.
        - factors: it takes into account the read-out system we are using (using string) and the amplification factor (int or float). Type List.
        - ranges: time values for the Range integration option. It should be introduced in seconds. Type List.
    """

    try:
        if factors[0] == "DAQ": factors[0] = 2 / 16384
        if factors[0] == "OSC": factors[0] = 1
        
        for run,ch,typ in product(my_runs["NRun"], my_runs["NChannel"], types):
            ave = my_runs[run][ch][ref]
            for i in range(len(ave)):
                # x = my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch]["AnaADC"][0]))
                if typ == "ChargeAveRange":
                    i_idx,f_idx = find_baseline_cuts(ave[i])
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["ADC"][:,i_idx:f_idx],axis=1)*factors[0]/factors[1]*1e12
                if typ == "ChargeRange":
                    i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["ADC"][:,i_idx:f_idx],axis=1)*factors[0]/factors[1]*1e12
            print("Integrated wvfs according to %s baseline integration limits"%ref)
    
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs