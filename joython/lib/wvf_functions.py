# Dedicated library to perform average waveforms of the run
# the idea is to always call numpy.mean(ADCs,axis=1). We'll use 
# optimized functions to first shift the ADC arrays if alignement 
# is necessary 

import numpy as np
import numba

def compute_AverageWaveforms(Vars,Pretrigger=0.2):
    """Interface to call the 3 different modes to compute avg waveforms"""

    ADC, peak_vars = Vars
    centering_bin=int(ADC.shape[1]*Pretrigger)
    av_wv_vars=dict();
    av_wv_vars["AvWvf"]=Average_waveform(ADC);
    av_wv_vars["AvWvf_Center_Peak"]=Average_waveform(ADC,"shifted",centering_bin-peak_vars["PeakTime"]);
    av_wv_vars["AvWvf_Center_Rise"]=Average_waveform(ADC,"shifted",centering_bin-peak_vars["RiseTime"]);
    return av_wv_vars;

def Average_waveform(ADC,mode="simple",shift=None):
    """Template function computing average waveform for a fixed channel

    Args:
        ADCs (numpy.ndarray): ADC input must be a 2D array, where every row is a waveform
        mode (str): simple=no shift, if alignement necessary use shifted instead.
        shift (numpy.ndarray): If present, Must be a numpy 1Darray, with entries equal to number of rows of input wvf 
    
    Returns:
        Average WVF(NDArray): np array with number of entries equal to number of columns of input ADCs
    """
    ADCs=ADC
    if type(ADC)==tuple: #more arguments given
        ADCs,mode,shift=ADC

    if mode=="simple":
        return np.mean(ADCs,axis=0) #Good ol mean
    
    elif mode == "shifted":
        N_wvfs=ADCs.shape[0]
        aux_ADC=np.zeros(ADCs.shape)
        for i in range(N_wvfs):
            aux_ADC[i]=shift4_numba(ADCs[i],int(shift[i])) # Shift the wvfs
        
        return Average_waveform(aux_ADC) #once aligned, call simple mode
    else:
        Exception

# eficient shifter (c/fortran compiled); https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
@numba.njit
def shift4_numba(arr, num, fill_value=0):#default shifted value is 0, remember to always substract your pedestal first
    if   num > 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:#no shift
        return arr

@numba.njit
def shift_ADCs(ADC,shift):
        N_wvfs=ADC.shape[0]
        aux_ADC=np.zeros(ADC.shape)
        for i in range(N_wvfs):
            aux_ADC[i]=shift4_numba(ADC[i],int(shift[i])) # Shift the wvfs
        return aux_ADC;