#================================================================================================================================================#
# This library contains functions to compute variables from the raw data. They are mostky used in the *Process.py macros.                        #
#================================================================================================================================================#

import numpy as np
import numba
from itertools import product
# from scipy     import stats as st

#===========================================================================#
#************************ GENERAL FUNCTIONS ********************************#
#===========================================================================# 

def insert_variable(my_runs, var, key, debug = False):
    '''
    Insert values for each type of signal.
    '''

    # Import from other libraries
    from .io_functions import print_colored

    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        i = np.where(np.array(my_runs["NRun"]).astype(int) == run)[0][0]
        j = np.where(np.array(my_runs["NChannel"]).astype(int) == ch)[0][0]

        try: my_runs[run][ch][key] = var[j]
        except KeyError: 
            if debug: print_colored("Inserting value...", "DEBUG")

def generate_cut_array(my_runs,debug=False):
    '''
    This function generates an array of bool = True with length = NEvts. 
    If cuts are applied and then you run this function, it resets the cuts.
    '''

    # Import from other libraries
    from .io_functions import print_colored

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):    
        if debug: print_colored("Keys in my_run before generating cut array: " +str(my_runs[run][ch].keys()), "DEBUG")
        for key in my_runs[run][ch].keys():
            # if debug: print("Output of find function for key: ",key,key.find("ADC"))
            # if key.find("ADC") == 0:
            if "ADC" in key:      ADC_key = key
            elif "Charge" in key: ADC_key = key
            elif "Peak" in key:   ADC_key = key
        my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][ADC_key]),dtype=bool)
        if debug: print_colored("Keys in my_run after generating cut array: "+str(my_runs[run][ch].keys()), "DEBUG")

def get_units(my_runs, debug = False):
    '''
    Computes and store in a dictionary the units of each variable.  
    '''

    for run, ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        keys = my_runs[run][ch].keys()
        aux_dic = {}
        for key in keys:
            if "Amp" in key or "Ped" in key or "ADC" in key: aux_dic[key] = "ADC"
            elif "Time" in key or "Sampling" in key:         aux_dic[key] = "s"
            elif "Charge" in key:                            aux_dic[key] = "pC"
            else:                                            aux_dic[key] = "a.u."
            
        my_runs[run][ch]["UnitsDict"] = aux_dic

#===========================================================================#
#************************* PEAK + PEDESTAL *********************************#
#===========================================================================# 

def compute_peak_variables(my_runs, key = "ADC", label = "", debug = False):
    '''
    Computes the peaktime and amplitude of a collection of a run's collection in standard format
    '''
    
    # Import from other libraries
    from .io_functions import print_colored

    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            my_runs[run][ch][label+"PeakAmp" ] = np.max    (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
            my_runs[run][ch][label+"PeakTime"] = np.argmax (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
            print_colored("Peak variables have been computed for run %i ch %i"%(run,ch), "blue")
        except KeyError: 
            if debug: print_colored("*EXCEPTION: for %i, %i, %s peak variables could not be computed"%(run,ch,key), "WARNING")

def compute_pedestal_variables(my_runs, key = "ADC", label = "", buffer = 200, debug = False):
    '''
    Computes the pedestal variables of a collection of a run's collection in standard format
    '''

    # Import from other libraries
    from .io_functions import print_colored

    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            # ped_lim = st.mode(my_runs[run][ch][label+"PeakTime"], keepdims=True)[0][0]-buffer # Deprecated function
            values,counts = np.unique(my_runs[run][ch][label+"PeakTime"], return_counts=True)
            ped_lim = values[np.argmax(counts)]-buffer
            if ped_lim < 0: ped_lim = 200
            my_runs[run][ch][label+"PedSTD"]  = np.std (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMean"] = np.mean(my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMax"]  = np.max (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedMin"]  = np.min (my_runs[run][ch][key][:,:ped_lim],axis=1)
            my_runs[run][ch][label+"PedLim"]  = ped_lim
            # my_runs[run][ch][label+"PedRMS"]  = np.sqrt(np.mean(np.abs(my_runs[run][ch][key][:,:ped_lim]**2),axis=1))
            print_colored("Pedestal variables have been computed for run %i ch %i"%(run,ch), "blue")
        except KeyError: 
            if debug: print_colored("*EXCEPTION: for %i, %i, %s pedestal variables could not be computed"%(run,ch,key), "WARNING")

def compute_pedestal_variables_sliding_window(my_runs, key = "ADC", label = "", ped_lim = 400,sliding=50,pretrigger=800, start = 0, debug = False):
    '''
    Computes the pedestal variables of a collection of a run's collection in several windows.
    
    **VARIABLES:**

    - label: string added to the new variables. Eg: label = Raw, variable = PedSTD --> RawPedSTD
    - ped_lim: size in bins of the sliding window
    - sliding: bins moved between shifts of the window
    - pretrigger: amount of bins to study. Eg: ped_lim = 400, sliding = 50, pretrigger = 800 --> 8 windows to compute
    - start: the bin where starts the window. This way you can check the end of the window
    '''
    
    # Import from other libraries
    from .io_functions import print_colored
    
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        try:
            ADCs_aux=my_runs[run][ch][key]
            ADCs_s=compute_pedestal_sliding_windows(ADCs_aux,ped_lim=ped_lim,sliding=sliding,pretrigger=pretrigger)
            
            my_runs[run][ch][label+"PedSTD"]  = np.std (ADCs_s[:,start:(start+ped_lim)],axis=1)
            my_runs[run][ch][label+"PedMean"] = np.mean(ADCs_s[:,start:(start+ped_lim)],axis=1)
            my_runs[run][ch][label+"PedMax"]  = np.max (ADCs_s[:,start:(start+ped_lim)],axis=1)
            my_runs[run][ch][label+"PedMin"]  = np.min (ADCs_s[:,start:(start+ped_lim)],axis=1)
            my_runs[run][ch][label+"PedLim"]  = ped_lim
            # my_runs[run][ch][label+"PedRMS"]  = np.sqrt(np.mean(np.abs(ADCs_s[:,start:(start+ped_lim)]**2),axis=1))
            print_colored("Pedestal variables have been computed for run %i ch %i"%(run,ch), "blue")
        except KeyError: 
            if debug: print_colored("*EXCEPTION: for %i, %i, %s pedestal variables could not be computed"%(run,ch,key), "WARNING")

def compute_pedestal_sliding_windows(ADC,ped_lim=400,sliding=50,pretrigger=800, start = 0):
    '''
    Taking the best between different windows in pretrigger. Same variables than "compute_pedestal_variables_sliding_window".
    It checks for the best window.
    '''
    
    pedestal_vars=dict();
    slides=int((pretrigger-ped_lim)/sliding);
    N_wvfs=ADC.shape[0];
    aux=np.zeros((N_wvfs,slides))
    for i in range(slides): aux[:,i]=np.std (ADC[:,(i*sliding+start):(i*sliding+ped_lim+start)],axis=1)
    #put first in the wvf the appropiate window, the one with less std:
    shifts= np.argmin (aux,axis=1)*(-1)*sliding
    ADC_s = shift_ADCs(ADC,shifts)
    #compute all ped variables, now with the best window available

    return ADC_s

def compute_ana_wvfs(my_runs, debug = False):
    '''
    Computes the peaktime and amplitude of a collection of a run's collection in standard format
    '''
    # Import from other libraries
    from .io_functions import print_colored, print_keys

    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):

        my_runs[run][ch]["ADC"] = my_runs[run][ch]["RawPChannel"]*((my_runs[run][ch]["RawADC"].T-my_runs[run][ch]["RawPedMean"]).T)
        print_colored("Analysis wvfs have been computed for run %i ch %i"%(run,ch), "blue")
        if debug: print_keys(my_runs)

        del my_runs[run][ch]["RawADC"] # After ADC is computed, delete RawADC from memory

def compute_power_spec(ADC, timebin, debug = False):
    ''' 
    Computes the power spectrum of the given events. It returns both axis. 
    '''

    aux = [] 
    aux_X = np.fft.rfftfreq(len(ADC[0]), timebin)
    for i in range(len(ADC)): aux.append(np.fft.rfft(ADC[i]))

    return np.absolute(np.mean(aux, axis = 0)), np.absolute(aux_X)


@numba.njit
def shift_ADCs(ADC,shift):
    ''' 
    Used for the sliding window. 
    '''

    N_wvfs=ADC.shape[0]
    aux_ADC=np.zeros(ADC.shape)
    for i in range(N_wvfs): aux_ADC[i]=shift4_numba(ADC[i],int(shift[i])) # Shift the wvfs
    
    return aux_ADC

# eficient shifter (c/fortran compiled); https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
@numba.njit
def shift4_numba(arr, num, fill_value=0): #default shifted value is 0, remember to always substract your pedestal first
    ''' 
    Used for the sliding window.
    '''

    if   num > 0: return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0: return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:         return arr #no shift