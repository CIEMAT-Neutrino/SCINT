# Dedicated library to perform average waveforms of the run
# the idea is to always call numpy.mean(ADCs,axis=1). We'll use 
# optimized functions to first shift the ADC arrays if alignement 
# is necessary 

import numpy as np

def Average_waveform(ADC):
    """Template function computing average waveform for a fixed channel

    Args:
        ADCs (numpy.ndarray): ADC input must be a 2D array, where every row is a waveform
        mode (str): simple=no shift, if alignement necessary use shifted instead.
        shift (numpy.ndarray): If present, Must be a numpy 1Darray, with entries equal to number of rows of input wvf 
    
    Returns:
        Average WVF(NDArray): np array with number of entries equal to number of columns of input ADCs
    """
    ADCs=ADC
    if type(ADC)==tuple:
        ADCs,mode,shift=ADC
        print(mode)
    if mode=="simple":
        return np.mean(ADCs,axis=0) #Good ol mean
    
    elif mode == "shifted":
        print("debugg")
        N_wvfs=len(ADCs)
        for i in range(N_wvfs):
            print(int(shift[i]))
            ADCs[i]=shift4_numba(ADCs[i],int(shift[i])) # Shift the wvfs
        
        return Average_waveform(ADCs) #once aligned, call simple mode
    else:
        Exception










# eficient shifter (c/fortran compiled); https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
import numba

@numba.njit
def shift4_numba(arr, num, fill_value=0):#default shifted value is 0, remember to always substract your pedestal first
    if num >= 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    else:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))