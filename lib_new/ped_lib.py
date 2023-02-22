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
    adc_raw, pedestal , polarity= Vars
    
    
    a=adc_raw.T
    b=pedestal["MEAN"].T
    
    adc_raw=ne.evaluate( '(a-b)*polarity').T #optimizing, multithreading

    return adc_raw;