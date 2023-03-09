import numpy as np
from lib.wvf_functions import shift_ADCs

def compute_ChargeRange(ADC,low=500,high=4000):
    
    #Fixed size in window
    charge_vars=dict();
    peak_time=np.argmax (ADC    ,axis=1)
    charge_vars["ChargeRange"]   = np.sum (ADC[:,low:high],axis=1)

    Pretrigger=0.2
    centering_bin=int(ADC.shape[1]*Pretrigger)
    shifted=shift_ADCs(ADC,shift=centering_bin-peak_time)

    #Fixed size wrt the peak
    charge_vars["ChargePeakRange"]   = np.sum (shifted[:,centering_bin-500:high],axis=1)

    return charge_vars;

