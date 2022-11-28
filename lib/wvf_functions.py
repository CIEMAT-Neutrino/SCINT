# import copy
import numpy as np
import matplotlib.pyplot as plt

from .io_functions import check_key, print_keys
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

def average_wvfs(my_runs, OPT={}, threshold=50, PATH="../data/ave/"):
    """
    It calculates the average waveform of a run in three different ways:
        - AveWvf: each event is added without centering
        - AvWvfPeak: 
        - AvWvfThreshold: 
    LA VERDAD NO ENTIENDO ESTA FUNCIÓN CHICO
    """

    for run,ch in product(my_runs["NRun"], my_runs["NChannel"]):
        try:
            
            # No centering
            aux_ADC = my_runs[run][ch]["AnaADC"]
            my_runs[run][ch]["AveWvf"] = [np.mean(aux_ADC,axis=0)]
            
            # aux_path=PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            
            # centering
            bin_ref          = np.argmax(aux_ADC[0]) #using the first peak as reference
            # bin_ref         = int(len(aux_ADC[0])/15) #10% of time window
            av_wvf_peak      = np.zeros(aux_ADC[0].shape)
            av_wvf_threshold = np.zeros(aux_ADC[0].shape)

            n_wvs   = len(aux_ADC)
            n_bins  = len(aux_ADC[0])
            
            for wvf in aux_ADC:
                
                bin_peak          = np.argmax(wvf)
                
                try:
                    bin_threshold = np.argwhere(wvf>threshold)[0][0]
                except:
                    #no good value found;
                    bin_threshold = n_bins

                # Peak centering
                if bin_ref < bin_peak:
                    av_wvf_peak[:bin_ref]                    += (wvf[(bin_peak-bin_ref):bin_peak]/n_wvs);
                    av_wvf_peak[bin_ref:-(bin_peak-bin_ref)] += (wvf[bin_peak:]/n_wvs);
                else:
                    av_wvf_peak[(bin_ref-bin_peak):bin_ref]  += (wvf[:bin_peak]/n_wvs);
                    av_wvf_peak[bin_ref:-1]                  += (wvf[bin_peak:-(bin_ref-bin_peak+1)]/n_wvs);
                
                # threshold centering
                if bin_ref<bin_threshold:
                    av_wvf_threshold[:bin_ref]               += (wvf[(bin_threshold-bin_ref):bin_threshold]/n_wvs);
                    av_wvf_threshold[bin_ref:-(bin_threshold-bin_ref)]  += (wvf[bin_threshold:]/n_wvs);
                else:
                    av_wvf_threshold[(bin_ref-bin_threshold):bin_ref]   += (wvf[:bin_threshold]/n_wvs);
                    av_wvf_threshold[bin_ref:-1]             += (wvf[bin_threshold:-(bin_ref-bin_threshold+1)]/n_wvs);
            
            if check_key(OPT,"PRINT_KEYS") == True and OPT["PRINT_KEYS"] == True: print_keys(my_runs)
            
            my_runs[run][ch]["AvWvfPeak"]      = [av_wvf_peak]
            my_runs[run][ch]["AvWvfThreshold"] = [av_wvf_threshold]
            # del my_runs[run][ch]["ADC"]

            # np.save(aux_path,my_runs[run][ch])
            # print("Saved data in:" , aux_path)

        except KeyError:
            print("Empty dictionary. No average to compute.")

def average_SPE_wvfs(my_runs, out_runs, key, OPT={}):
    """
    It computes the average waveform of a single photoelectron. Previously, we have to calculate the charge histogram and check the SPE charge limits.
    This function takes those values to isolate the SPE events.
    VARIABLES:
        - my_runs: run(s) we want to use
        - out_runs: indicate the .npy where we want to save the average waveform.
        - key:
        - OPT: 
    """

    for run,ch,key in product(my_runs["NRun"], my_runs["NChannel"], key):
        try:
        
            aux_ADC = np.zeros(len(my_runs[run][ch]["AnaADC"][0]))
            counter = 0
            
            min_charge = my_runs[run][ch]["SPEMinCharge"]
            max_charge = my_runs[run][ch]["SPEMaxCharge"]
            
            for i in range(len(my_runs[run][ch]["AnaADC"])):

                # Check charge in SPE range
                if min_charge < my_runs[run][ch][key][i] < max_charge:
                    aux_ADC = aux_ADC + my_runs[run][ch]["AnaADC"][i]
                    counter = counter + 1    

            out_runs[run][ch]["SPEAvWvf"] = [aux_ADC/counter]
            
            if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
                plt.plot(4e-9*np.arange(len(out_runs[run][ch]["SPEAvWvf"])),out_runs[run][ch]["SPEAvWvf"])
                plt.show()
            if check_key(OPT,"PRINT_KEYS") == True and OPT["PRINT_KEYS"] == True: print_keys(my_runs)
            
        except KeyError:
            print("Empty dictionary. No average_SPE to compute.")

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
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["AnaADC"][:,i_idx:f_idx],axis=1)*factors[0]/factors[1]*1e12
                if typ == "ChargeRange":
                    i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                    my_runs[run][ch][typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["AnaADC"][:,i_idx:f_idx],axis=1)*factors[0]/factors[1]*1e12
            print("Integrated wvfs according to %s baseline integration limits"%ref)
    
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs