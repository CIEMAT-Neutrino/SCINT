# import copy
import numpy as np
import matplotlib.pyplot as plt

from .io_functions import check_key, print_keys
from itertools import product

def find_baseline_cuts(RAW):
    """
    It finds the cuts with the x-axis. It returns the index of both bins.
    VARIABLE:
        - RAW: the .root that you want to analize.
    """
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

def average_wvfs(my_runs,OPT={},threshold=50,PATH="../data/ave/"):
    """
    It calculates the average waveform of a run in three different ways:
        - AvWvf: each event is added without centering
        - AvWvf_peak: 
        - AvWvf_threshold: 
    LA VERDAD NO ENTIENDO ESTA FUNCIÓN CHICO
    """

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        try:
            
            # No centering
            aux_ADC = my_runs[run][ch]["Ana_ADC"]
            my_runs[run][ch]["AvWvf"] = [np.mean(aux_ADC,axis=0)]
            
            # aux_path=PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            
            # centering
            bin_ref         =np.argmax(aux_ADC[0]) #using the first peak as reference
            # bin_ref         =int(len(aux_ADC[0])/15) #10% of time window
            av_wvf_peak      =np.zeros(aux_ADC[0].shape)
            av_wvf_threshold =np.zeros(aux_ADC[0].shape)

            n_wvs   =len(aux_ADC)
            n_bins  =len(aux_ADC[0])
            
            for wvf in aux_ADC:
                
                bin_peak      = np.argmax(wvf)
                
                try:
                    bin_threshold = np.argwhere(wvf>threshold)[0][0]
                except:
                    #no good value found;
                    bin_threshold=n_bins

                # Peak centering
                if bin_ref<bin_peak:
                    av_wvf_peak[:bin_ref]                    += (wvf[(bin_peak-bin_ref):bin_peak]/n_wvs);
                    av_wvf_peak[bin_ref:-(bin_peak-bin_ref)] += (wvf[bin_peak:]/n_wvs);
                else:
                    av_wvf_peak[(bin_ref-bin_peak):bin_ref] += (wvf[:bin_peak]/n_wvs);
                    av_wvf_peak[bin_ref:-1]                   += (wvf[bin_peak:-(bin_ref-bin_peak+1)]/n_wvs);
                
                # threshold centering
                if bin_ref<bin_threshold:
                    av_wvf_threshold[:bin_ref]                    += (wvf[(bin_threshold-bin_ref):bin_threshold]/n_wvs);
                    av_wvf_threshold[bin_ref:-(bin_threshold-bin_ref)] += (wvf[bin_threshold:]/n_wvs);
                else:
                    av_wvf_threshold[(bin_ref-bin_threshold):bin_ref] += (wvf[:bin_threshold]/n_wvs);
                    av_wvf_threshold[bin_ref:-1]                   += (wvf[bin_threshold:-(bin_ref-bin_threshold+1)]/n_wvs);
            
            if check_key(OPT,"PRINT_KEYS") == True and OPT["PRINT_KEYS"] == True: print_keys(my_runs)
            
            my_runs[run][ch]["AvWvf_peak"]      = [av_wvf_peak]
            my_runs[run][ch]["AvWvf_threshold"] = [av_wvf_threshold]
            # del my_runs[run][ch]["ADC"]

            # np.save(aux_path,my_runs[run][ch])
            # print("Saved data in:" , aux_path)

        except KeyError:
            print("Empty dictionary. No average to compute.")

def average_SPE_wvfs(my_runs,out_runs,KEY,OPT={}):
    """
    It computes the average waveform of a single photoelectron. Previously, we have to calculate the charge histogram and check the SPE charge limits.
    This function takes those values to isolate the SPE events.
    VARIABLES:
        - my_runs: run(s) we want to use
        - out_runs: indicate the .npy where we want to save the average waveform.
        - KEY:
        - OPT: 
    """

    for run,ch,key in product(my_runs["N_runs"],my_runs["N_channels"],KEY):
        try:
        
            aux_ADC = np.zeros(len(my_runs[run][ch]["Ana_ADC"][0]))
            counter = 0
            
            min_charge = my_runs[run][ch]["SPE_min_charge"]
            max_charge = my_runs[run][ch]["SPE_max_charge"]
            
            for i in range(len(my_runs[run][ch]["Ana_ADC"])):

                # Check charge in SPE range
                if min_charge < my_runs[run][ch][key][i] < max_charge:
                    aux_ADC = aux_ADC + my_runs[run][ch]["Ana_ADC"][i]
                    counter = counter + 1    

            out_runs[run][ch]["SPE_AvWvf"] = [aux_ADC/counter]
            
            if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
                plt.plot(4e-9*np.arange(len(out_runs[run][ch]["SPE_AvWvf"])),out_runs[run][ch]["SPE_AvWvf"])
                plt.show()
            if check_key(OPT,"PRINT_KEYS") == True and OPT["PRINT_KEYS"] == True: print_keys(my_runs)
            
        except KeyError:
            print("Empty dictionary. No average_SPE to compute.")

def expo_average(my_run,alpha):
    v_averaged=np.zeros(len(my_run))
    v_averaged[0]=my_run[0]
    for i in range (len(my_run)-1):
        v_averaged[i+1]=(1-alpha)*v_averaged[i]+alpha*my_run[i+1]
    return v_averaged

def unweighted_average(my_run):
    v_averaged=np.zeros(len(my_run))
    v_averaged[0]=my_run[0]
    v_averaged[-1]=my_run[-1]

    for i in range (len(my_run)-2):
        v_averaged[i+1]=(my_run[i]+my_run[i+1]+my_run[i+2])/3
    return v_averaged

def smooth(my_run,alpha):
    my_run=expo_average(my_run,alpha)
    my_run=unweighted_average(my_run)
    return my_run

def integrate_wvfs(my_runs,types,ref,FACTORS,RANGES):  

    try:
        if FACTORS[0] == "DAQ": FACTORS[0] = 2/16384
        if FACTORS[0] == "OSC": FACTORS[0] = 1
        
        for run,ch,typ in product(my_runs["N_runs"],my_runs["N_channels"],types):
            AVE = my_runs[run][ch][ref]
            for i in range(len(AVE)):
                # x = my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch]["Ana_ADC"][0]))
                if typ == "Ave_Limits":
                    i_idx,f_idx = find_baseline_cuts(AVE[i])
                    my_runs[run][ch]["Charge_"+typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["Ana_ADC"][:,i_idx:f_idx],axis=1)*FACTORS[0]/FACTORS[1]*1e12
                if typ == "Range":
                    i_idx = int(np.round(RANGES[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(RANGES[1]/my_runs[run][ch]["Sampling"]))
                    my_runs[run][ch]["Charge_"+typ] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["Ana_ADC"][:,i_idx:f_idx],axis=1)*FACTORS[0]/FACTORS[1]*1e12
            print("Integrated wvfs according to %s baseline integration limits"%ref)
    
    except KeyError:
        print("Empty dictionary. No integration to compute.")

    return my_runs