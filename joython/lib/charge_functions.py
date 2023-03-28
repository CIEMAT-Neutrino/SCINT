import numpy as np
from numba import njit
from lib.wvf_functions import shift_ADCs

def compute_ChargeRange(ADC,low=250,high=2000):
    
    ## All waveformsm, same range
    
    #Fixed size in window
    charge_vars=dict();
    peak_time=np.argmax (ADC    ,axis=1)
    charge_vars["ChargeRange"]   = np.sum (ADC[:,low:high],axis=1)

    Pretrigger=0.2
    centering_bin=int(ADC.shape[1]*Pretrigger)
    shifted=shift_ADCs(ADC,shift=centering_bin-peak_time)

    #Fixed size wrt the peak
    charge_vars["ChargePeakRange"]   = np.sum (shifted[:,centering_bin-low:centering_bin+high],axis=1)
    
    #Fixed size, set by average wvf cuantities. Requires pedestal subtraction first to make sense.
    average_wvf=np.mean(ADC,axis=0);
    RELATIVE_AMPLITUDE=0.01;
    left, right = find_bins(average_wvf,RELATIVE_AMPLITUDE);
    charge_vars["ChargeRangeAverageWvf"]   = np.sum (ADC[:,left:right],axis=1);
    
    ## Waveform by waveform

    #from peak to 1% of max amplitude
    charge_vars["ChargeRangeRelativeAmp"] =sum_near_maximum(ADC)
    
    #from peak to 0% of max amplitude (back to baseline)
    charge_vars["ChargeRangePed"] =sum_near_maximum(ADC,relative_amplitude=0.)
    
    # Mixed approach (peakfinder-like), in given range, look for max above threshold (SPE), 
    # then integrate the pulse until tolerance relative amplitude to the max is found, 
    # then look for next peak and repeat until no peak above threshold is found
    charge_vars["PeakFinderInRange"]=fin_peaks_above_threshold_and_sum_near_maximum(shifted,relative_amplitude=0.01,threshold=12,bmin=800,bmax=1100)
    return charge_vars;



import numpy as np

@njit
def sum_near_maximum(ADC, relative_amplitude=0.01):
    n_rows, n_cols = ADC.shape
    result = np.zeros(n_rows)
    
    for i in range(n_rows):
        max_index = np.argmax(ADC[i])
        threshold = ADC[i, max_index] * relative_amplitude
        total = 0
        
        for j in range(max_index, n_cols):
            if ADC[i, j] >= threshold:
                total += ADC[i, j]
            else:
                break
                
        for j in range(max_index-1, -1, -1):
            if ADC[i, j] >= threshold:
                total += ADC[i, j]
            else:
                break
        
        result[i] = total
        
    return result

import numpy as np
from numba import njit


@njit
def fin_peaks_above_threshold_and_sum_near_maximum(ADC, relative_amplitude, threshold, bmin, bmax):
    result = np.zeros(ADC.shape[0], dtype=np.float64)

    for i in range(ADC.shape[0]):
        subarr = ADC[i, bmin:bmax]
        while True:
            max_index = np.argmax(subarr)
            if subarr[max_index] < threshold:
                break
            start_index = max_index
            while start_index >= 0 and subarr[start_index] >= threshold:
                start_index -= 1
            end_index = max_index
            while end_index < len(subarr) and subarr[end_index] >= threshold:
                end_index += 1
            amplitude = subarr[max_index] * relative_amplitude
            subsum = 0.0
            for j in range(start_index + 1, max_index+1):
                if subarr[j] >= threshold and subarr[j] > amplitude - subsum:
                    subsum += subarr[j]
                    subarr[j] = 0.0
            result[i]+=subsum;
            subsum = 0.0
            for j in range(max_index + 1, end_index):
                if subarr[j] >= threshold and subarr[j] > amplitude - subsum:
                    subsum += subarr[j]
                    subarr[j] = 0.0
            result[i]+=subsum;

    return result

from numba import njit


@njit
def find_bins(arr, rel_amp):
    """
    Finds the first bin to the left and right of the maximum value in the array that has a value equal to or
    lower than the maximum times the relative amplitude value.
    
    Parameters:
    arr (numpy.ndarray): A 1D numpy array.
    rel_amp (float): A relative amplitude value.
    
    Returns:
    left_bin (int): The index of the first bin to the left of the maximum value that satisfies the condition.
    right_bin (int): The index of the first bin to the right of the maximum value that satisfies the condition.
    """
    max_val = arr.max()
    threshold = max_val * rel_amp
    
    left_bin = 0
    for i in range(arr.argmax(), -1, -1):
        if arr[i] <= threshold:
            left_bin = i
            break
    
    right_bin = arr.size - 1
    for i in range(arr.argmax(), arr.size):
        if arr[i] <= threshold:
            right_bin = i
            break
    
    return left_bin, right_bin