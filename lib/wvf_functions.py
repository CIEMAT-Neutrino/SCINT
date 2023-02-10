import numpy as np
import matplotlib.pyplot as plt

from scipy import stats as st
from .io_functions import check_key
from .ana_functions import generate_cut_array, get_units
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
            if check_key(my_runs[run][ch], "UnitsDict") == False:
                get_units(my_runs)

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

def integrate_wvfs(my_runs, info = {}, key = "ADC"):
    """
    This function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    VARIABLES:
        - my_runs: run(s) we want to use
        - info: input information from .txt with DAQ characteristics and Charge Information.
        - key: waveform we want to integrate
    In txt Charge Info part we can indicate the type of integration, the reference average waveform and the ranges we want to integrate.
    If I_RANGE = -1 it fixes t0 to pedestal time and it integrates the time indicated in F_RANGE, e.g. I_RANGE = -1 F_RANGE = 6e-6 it integrates 6 microsecs from pedestal time.
    If I_RANGE != -1 it integrates from the indicated time to the F_RANGE value, e.g. I_RANGE = 2.1e-6 F_RANGE = 4.3e-6 it integrates in that range.
    I_RANGE must have same length than F_RANGE!
    """

    try:
        conversion_factor = info["DYNAMIC_RANGE"][0] / info["BITS"][0] # Amplification factor of the system
        channels = []; channels = np.append(channels,info["CHAN_STNRD"])
        ch_amp = dict(zip(channels,info["CHAN_AMPLI"])) # Creates a dictionary with amplification factors according to each detector
        i_range = info["I_RANGE"] # Get initial time(s) to start the integration
        f_range = info["F_RANGE"] # Get final time(s) to finish the integration
        
        for run,ch,typ,ref in product(my_runs["NRun"], my_runs["NChannel"], info["TYPE"], info["REF"]):
            ave = my_runs[run][ch][ref] # Load the reference average waveform
            my_runs[run][ch]["ChargeRangeInfo"] = {} # Creates a dictionary with ranges for each ChargeRange entry
            for i in range(len(ave)):
                if typ == "ChargeAveRange":
                    i_idx,f_idx = find_baseline_cuts(ave[i])
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch][key][:,i_idx:f_idx],axis=1) * conversion_factor/ch_amp[ch]*1e12
            if my_runs[run][ch]["Label"]=="SC" and key =="ADC": break # Avoid range integration for SC (save time)
            if typ.startswith("ChargeRange"):
                for j in range(len(f_range)):
                    my_runs[run][ch][typ+str(j)] = []
                    if i_range[j] == -1: # Integration with fixed ranges
                        t0 = my_runs[run][ch]["PedLim"]*my_runs[run][ch]["Sampling"]
                        tf = my_runs[run][ch]["PedLim"]*my_runs[run][ch]["Sampling"] + f_range[j]
                    else: # Integration with custom ranges
                        t0 = i_range[j]; tf = f_range[j]
                    i_idx = int(np.round(t0/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(tf/my_runs[run][ch]["Sampling"]))
                    my_runs[run][ch][typ+str(j)]= my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch][key][:,i_idx:f_idx], axis = 1) * conversion_factor/ch_amp[ch]*1e12
                    
                    new_key = {typ+str(j): [t0,tf]}
                    my_runs[run][ch]["ChargeRangeDict"].update(new_key) # Update the dictionary
            print("Integrated wvfs according to %s baseline integration limits"%info["REF"][0])
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs

def charge_nevents(my_runs, keys = ["ChargeAveRange"]):
    """
    This function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    VARIABLES:
        - my_runs: run(s) we want to use
        - info: input information from .txt with DAQ characteristics and Charge Information.
        - key: waveform we want to integrate
    In txt Charge Info part we can indicate the type of integration, the reference average waveform and the ranges we want to integrate.
    If I_RANGE = -1 it fixes t0 to pedestal time and it integrates the time indicated in F_RANGE, e.g. I_RANGE = -1 F_RANGE = 6e-6 it integrates 6 microsecs from pedestal time.
    If I_RANGE != -1 it integrates from the indicated time to the F_RANGE value, e.g. I_RANGE = 2.1e-6 F_RANGE = 4.3e-6 it integrates in that range.
    I_RANGE must have same length than F_RANGE!
    """

    try:
        for run,ch,key in product(my_runs["NRun"], my_runs["NChannel"], keys):
            runtime = (my_runs[run][ch]["TimeStamp"][-1] - my_runs[run][ch]["TimeStamp"][0]) #segundos
            my_runs[run][ch]["NEvents"+key] = my_runs[run][ch][key] / runtime
            print(my_runs[run][ch].keys())
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs
