import numpy as np
import numexpr as ne

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