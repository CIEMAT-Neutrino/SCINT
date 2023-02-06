# import copy
import numpy as np
import matplotlib.pyplot as plt

from scipy import stats as st
from .io_functions import check_key
from .ana_functions import generate_cut_array
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

            buffer = 100  
            mean_ana_ADC = np.mean(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True],axis=0)
            aux_ADC = my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True]
            bin_ref_peak = st.mode(np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True],axis=1), keepdims=True) #using the mode peak as reference
            bin_ref_peak = bin_ref_peak[0][0]
            
            # centering none
            if centering == "NONE":
                my_runs[run][ch]["AveWvf"+cut_label] = [mean_ana_ADC]
            
            # centering peak
            if centering == "PEAK":
                bin_max_peak = np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True][:,bin_ref_peak-buffer:bin_ref_peak+buffer],axis=1) 
                bin_max_peak = bin_max_peak + bin_ref_peak - buffer
                for ii in range(len(aux_ADC)):
                    aux_ADC[ii] = np.roll(aux_ADC[ii], bin_max_peak[ii] - bin_ref_peak)
                my_runs[run][ch]["AveWvfPeak"+cut_label] = [np.mean(aux_ADC,axis=0)]

            # centering thld
            if centering == "THRESHOLD":
                if threshold == 0: threshold = np.max(mean_ana_ADC)/2
                bin_ref_thld = st.mode(np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True]>threshold,axis=1), keepdims=True) #using the mode peak as reference
                bin_max_thld = np.argmax(my_runs[run][ch]["ADC"][my_runs[run][ch]["MyCuts"] == True][:,bin_ref_peak-buffer:bin_ref_peak+buffer]>threshold,axis=1)
                bin_max_peak = bin_max_thld + bin_ref_thld - buffer
                for ii in range(len(aux_ADC)):
                    aux_ADC[ii] = np.roll(aux_ADC[ii], bin_max_thld[ii] - bin_ref_thld)
                my_runs[run][ch]["AveWvfPeak"+cut_label] = [np.mean(aux_ADC,axis=0)]

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

def integrate_wvfs(my_runs, types, ref, ranges, info = {}):
    """
    This function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    VARIABLES:
        - my_runs: run(s) we want to use
        - types: indicates the way to make the integration. Type String.
            a) ChargeAveRange: it takes the average waveform and computes the values when the average crosses the baseline
            b) ChargeRange: it integrates in the time window specified by yourself in the vairable "ranges"
        - ref: STRING for key used as integration reference.
        - ranges: time values for the Range integration option. It should be introduced in seconds. Type List.
        - info: input information from .txt with DAQ characteristics
    """

    try:
        conversion_factor = info["DYNAMIC_RANGE"][0] / info["BITS"][0] # Amplification factor of the system
        channels = []; channels = np.append(channels,info["CHAN_STNRD"])
        ch_amp = dict(zip(channels,info["CHAN_AMPLI"])) # Creates a dictionary with amplification factors according to each detector

        for run,ch,typ in product(my_runs["NRun"], my_runs["NChannel"], types):
            ave = my_runs[run][ch][ref]
            for i in range(len(ave)):
                # x = my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch]["AnaADC"][0]))
                if typ == "ChargeAveRange":
                    i_idx,f_idx = find_baseline_cuts(ave[i])
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["ADC"][:,i_idx:f_idx],axis=1) * conversion_factor/ch_amp[ch]*1e12
                if typ.startswith("ChargeRange"):
                    i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["ADC"][:,i_idx:f_idx],axis=1) * conversion_factor/ch_amp[ch]*1e12
            print("Integrated wvfs according to %s baseline integration limits"%ref)
    
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs
