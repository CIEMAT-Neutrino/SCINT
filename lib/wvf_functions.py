# import copy
import numpy as np
import matplotlib.pyplot as plt

from .io_functions import check_key
from itertools import product

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

def average_wvfs(my_runs,threshold=50,PATH="../data/ave/"):

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        
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
        
        
        my_runs[run][ch]["AvWvf_peak"]      = [av_wvf_peak]
        my_runs[run][ch]["AvWvf_threshold"] = [av_wvf_threshold]
        # del my_runs[run][ch]["ADC"]

        # np.save(aux_path,my_runs[run][ch])
        # print("Saved data in:" , aux_path)

def average_SPE_wvfs(my_runs,out_runs,INT_KEY,OPT={}):

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        
        aux_ADC = np.zeros(len(my_runs[run][ch]["Ana_ADC"][0]))
        counter = 0
        
        min_charge = my_runs[run][ch]["SPE_min_charge"]
        max_charge = my_runs[run][ch]["SPE_max_charge"]
        
        for i in range(len(my_runs[run][ch]["Ana_ADC"])):

            # Check charge in SPE range
            if min_charge < my_runs[run][ch][INT_KEY][i] < max_charge:
                aux_ADC = aux_ADC + my_runs[run][ch]["Ana_ADC"][i]
                counter = counter + 1    

        out_runs[run][ch]["SPE_AvWvf"] = [aux_ADC/counter]
        
        if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
            plt.plot(4e-9*np.arange(len(out_runs[run][ch]["SPE_AvWvf"])),out_runs[run][ch]["SPE_AvWvf"])
            plt.show()

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

def integrate_wvfs(my_runs,TYPE,REF,PATH="../data/ana/"):  
    # AVE_RUNS = load_average_npy(my_runs["N_runs"],my_runs["N_channels"])
    
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        
        AVE = my_runs[run][ch][REF]
        i_idx,f_idx = find_baseline_cuts(AVE)
        # x = my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch]["Ana_ADC"][0]))
        
        if TYPE == "AVE_INT_LIMITS":
            my_runs[run][ch][TYPE] = my_runs[run][ch]["Sampling"]*np.sum(my_runs[run][ch]["Ana_ADC"][:,i_idx:f_idx],axis=1)
        
        # aux = dict()
        # for i in range(len(my_runs[runAna_ADC][ch]["ADC"])):
        #     RAW = my_runs[run][ch]["Ana_ADC"][i]
            
        #     if TYPE == "BASELINE_INT_LIMITS": 
        #         INT_I,INT_F = find_baseline_cuts(RAW)
            
        #     elif TYPE == "AVE_INT_LIMITS":
        #         INT_I,INT_F = i_idx,f_idx
        #     else: 
        #         print("INTEGRATION TYPE IS NOT DEFINED")
        #         sys.exit()
            
        #     aux[i] = np.trapz(RAW[INT_I:INT_F],x=4e-9*np.arange(len(RAW[INT_I:INT_F])))
        
        # my_runs[run][ch][TYPE] = aux
    return my_runs