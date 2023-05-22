import numpy as np
import numexpr as ne
from lib.wvf_functions import shift_ADCs

def compute_Pedestal(ADC,ped_lim=50):
    pedestal_vars=dict();
    pedestal_vars["STD"]   = np.std (ADC[:,:ped_lim],axis=1)
    pedestal_vars["MEAN"]  = np.mean(ADC[:,:ped_lim],axis=1)
    pedestal_vars["MAX"]   = np.max (ADC[:,:ped_lim],axis=1)
    pedestal_vars["Min"]   = np.min (ADC[:,:ped_lim],axis=1)

    return pedestal_vars;

def substract_Pedestal(Vars,pol=1):
    ADC_raw, pedestal , polarity= Vars
    
    
    a=ADC_raw.T
    b=pedestal["MEAN"].T
    
    ADC_raw=ne.evaluate( '(a-b)*polarity').T #optimizing, multithreading
    return ADC_raw;

def compute_Peak(ADC,thr=30):
    peak_vars=dict();
    peak_vars["Peak"]     = np.max    (ADC    ,axis=1)
    peak_vars["PeakTime"] = np.argmax (ADC    ,axis=1)
    peak_vars["RiseTime"] = np.argmax (ADC>thr,axis=1)

    return peak_vars;

def compute_Pedestal_slidingWindows(ADC,ped_lim=400,sliding=50,pretrigger=800):
    """Taking the best between different windows in pretrigger"""
    pedestal_vars=dict();
    slides=int((pretrigger-ped_lim)/sliding);
    N_wvfs=ADC.shape[0];
    aux=np.zeros((N_wvfs,slides))
    for i in range(slides):
        aux[:,i]=np.std (ADC[:,(i*sliding):(i*sliding+ped_lim)],axis=1)

    #put first in the wvf the appropiate window, the one with less std:
    shifts= np.argmin (aux,axis=1)
    shifts*=(-1)*sliding;#weird segmentation fault if used in line b4;
    ADC_s = shift_ADCs(ADC,shifts)

    #compute all ped variables, now with the best window available
    slided_ped_vars=compute_Pedestal(ADC_s,ped_lim)
    return slided_ped_vars;