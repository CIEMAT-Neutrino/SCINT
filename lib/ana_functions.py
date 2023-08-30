#================================================================================================================================================#
# This library contains functions to compute variables from the raw data. They are mostky used in the *Process.py macros.                        #
#================================================================================================================================================#

import numba
import numpy as np
from itertools import product

from .io_functions import print_colored

#===========================================================================#
#************************ GENERAL FUNCTIONS ********************************#
#===========================================================================# 

def insert_variable(my_runs, var, key, debug = False):
    '''
    Insert values for each type of signal.
    **VARIABLES**:
        - my_runs: dictionary containing the data
        - var:     array of values to be inserted
        - key:     key to be inserted
        - debug:   boolean to print debug messages
    '''
    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        i = np.where(np.array(my_runs["NRun"]).astype(int) == run)[0][0]
        j = np.where(np.array(my_runs["NChannel"]).astype(int) == ch)[0][0]

        try: my_runs[run][ch][key] = var[j]
        except KeyError: 
            if debug: print_colored("Inserting value...", "DEBUG")

def get_ADC_key(my_runs, key, debug = False):
    '''
    This function returns the ADC key for a given run.
    **VARIABLES**:
        - my_runs: dictionary containing the data
        - key:     key to be inserted
        - debug:   boolean to print debug messages
    '''
    found_duplicate = 0
    if key == "":
        for this_key in my_runs[my_runs["NRun"][0]][my_runs["NChannel"][0]].keys():
            if "ADC" in this_key:
                key = this_key
                label = this_key.split("ADC")[0]
                found_duplicate += 1
                if found_duplicate > 1:
                    print_colored("ERROR: Found more than one ADC key! Please check load preset.", "ERROR")
                    exit()
        if found_duplicate == 0:
            label = ""
            print_colored("WARNING: No ADC branch found!", "WARNING")
        if debug: print_colored("-> Found key: '%s' and label: '%s'"%(key,label), "SUCCESS")

    else:
        label = key.split("ADC")[0]
        print_colored("Returning label from provided key:", "INFO")
    
    return key, label

def get_wvf_label(my_runs, key, label, debug = False):
    '''
    This function returns the label for a given run. This depends on the found ADC key or the one provided by the user.
    **VARIABLES**:
        - my_runs: dictionary containing the data
        - key:     key to be inserted
        - label:   label to be inserted
        - debug:   boolean to print debug messages
    '''
    if key == "" and label == "":
        found_key, found_label = get_ADC_key(my_runs, key, debug = debug)
        out_key = found_key
        out_label = found_label

    elif key == "" and label != "":
        found_key, found_label = get_ADC_key(my_runs, key, debug = debug)
        out_key = found_key
        
        if found_label != label:
            print_colored("WARNING: Provided label does not match found label!", "WARNING")
            user_confirmation = input("Do you want to continue with coustom selection? [y/n]: ")
            if user_confirmation.lower() in ["y","yes"]:
                out_label = found_label
                print_colored("-> Selected label %s"%label, "SUCCESS")
            else:
                out_label = label
                print_colored("-> Found label %s"%found_label, "SUCCESS")

        else:
            out_label = found_label
            print_colored("-> Found label %s"%label, "SUCCESS")
    
    elif key != "" and label == "":
        print_colored("WARNING: Selected input ADC but no label provided!", "WARNING")
        found_key, found_label = get_ADC_key(my_runs, key, debug = debug)
        out_key = found_key
        out_label = found_label
        if found_label != key.split("ADC")[0]:
            print_colored("ERROR: Found label does not match label from provided key!", "ERROR")
            exit()
    
    else:
        print_colored("WARNING: Using full coustom mode for label and ADC key selection!", "WARNING")
        out_key = key
        out_label = label
    
    print_colored("-> Found label %s form key %s"%(out_label,out_key), "SUCCESS")
    return out_key, out_label
    
def generate_cut_array(my_runs, ref="", debug=False):
    '''
    This function generates an array of bool = True with length = NEvts. 
    If cuts are applied and then you run this function, it resets the cuts.
    **VARIABLES**:
        - my_runs: dictionary containing the data
        - ref:     reference variable to generate the cut array
        - debug:   boolean to print debug messages
    '''
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):    
        if debug: print_colored("Keys in my_run before generating cut array: " +str(my_runs[run][ch].keys()), "DEBUG")
        try:
            if ref == "": 
                key, label = get_wvf_label(my_runs, "", "", debug = debug)
                ref = key
            if debug: print("Check cut array ref: ",my_runs[run][ch][ref])
            my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][ref]),dtype=bool)
        
        except KeyError:
            print_colored("WARNING: Reference variable for cut array generation not found!", "WARNING")
            print("Searching for viable reference variable...")
            for key in my_runs[run][ch].keys():
                try:
                    if len(my_runs[run][ch][key]) > 1:
                        print_colored("Found viable reference variable: "+key, "WARNING")
                        my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][key]),dtype=bool)
                        break
                except TypeError:
                    if debug: print_colored("Key "+key+" is not a numpy array", "DEBUG")
                    pass
                except KeyError:
                    if debug: print_colored("Key "+key+" does not exist", "DEBUG")
                    pass
        
        if debug: print_colored("Keys in my_run after generating cut array: "+str(my_runs[run][ch].keys()), "DEBUG")

def get_units(my_runs, debug = False):
    '''
    Computes and store in a dictionary the units of each variable.  
    **VARIABLES**:
        - my_runs: dictionary containing the data
        - debug:   boolean to print debug messages
    '''
    if debug: print("Getting units...")
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        keys = my_runs[run][ch].keys()
        aux_dic = {}
        for key in keys:
            if "Amp" in key or "Ped" in key or "ADC" in key: aux_dic[key] = "ADC"
            elif "Time" in key or "Sampling" in key:         aux_dic[key] = "ticks"
            elif "Charge" in key:                            aux_dic[key] = "ADC x ticks"
            else:                                            aux_dic[key] = "a.u."
            
        my_runs[run][ch]["UnitsDict"] = aux_dic

#===========================================================================#
#************************* PEAK + PEDESTAL *********************************#
#===========================================================================# 

def compute_peak_variables(my_runs, key = "", label = "", debug = False):
    '''
    Computes the peaktime and amplitude of a collection of a run's collection in standard format
    '''
    key, label = get_wvf_label(my_runs, key, label, debug = debug)
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        my_runs[run][ch][label+"PeakAmp" ] = np.max    (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
        my_runs[run][ch][label+"PeakTime"] = np.argmax (my_runs[run][ch][key][:,:]*my_runs[run][ch][label+"PChannel"],axis=1)
        print_colored("Peak variables have been computed for run %i ch %i"%(run,ch), "blue")


def compute_pedestal_variables(my_runs, key="", label="", buffer=100, sliding=100, debug=False):
    '''
    Computes the pedestal variables of a collection of a run's collection in several windows.
    **VARIABLES:**
        - label: string added to the new variables. Eg: label = Raw, variable = PedSTD --> RawPedSTD
        - ped_lim: size in bins of the sliding window
        - sliding: bins moved between shifts of the window
        - pretrigger: amount of bins to study. Eg: ped_lim = 400, sliding = 50, pretrigger = 800 --> 8 windows to compute
        - start: the bin where starts the window. This way you can check the end of the window
    '''
    key, label = get_wvf_label(my_runs, key, label, debug = False)
    for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
        values,counts = np.unique(my_runs[run][ch][label+"PeakTime"], return_counts=True)
        ped_lim = values[np.argmax(counts)]-buffer
        
        ADC_aux=my_runs[run][ch][key]
        ADC, start_window=compute_pedestal_sliding_windows(ADC_aux, ped_lim=ped_lim, sliding=sliding)
        
        my_runs[run][ch][label+"PedSTD"]   = np.std (ADC[:,:sliding],axis=1)
        my_runs[run][ch][label+"PedMean"]  = np.mean(ADC[:,:sliding],axis=1)
        my_runs[run][ch][label+"PedMax"]   = np.max (ADC[:,:sliding],axis=1)
        my_runs[run][ch][label+"PedMin"]   = np.min (ADC[:,:sliding],axis=1)
        my_runs[run][ch][label+"PedLim"]   = ped_lim
        my_runs[run][ch][label+"PedStart"] = start_window
        my_runs[run][ch][label+"PedEnd"]   = start_window+sliding
        # my_runs[run][ch][label+"PedRMS"]  = np.sqrt(np.mean(np.abs(ADC[:,start:(start+ped_lim)]**2),axis=1))
        print_colored("Pedestal variables have been computed for run %i ch %i"%(run,ch), "blue")

def compute_pedestal_sliding_windows(ADC, ped_lim, sliding=100, debug=False):
    '''
    Taking the best between different windows in pretrigger. Same variables than "compute_pedestal_variables_sliding_window".
    It checks for the best window.
    '''
    
    slides=int(ped_lim/sliding);
    nwvfs=ADC.shape[0];
    aux=np.zeros((nwvfs,slides))

    for i in range(slides): aux[:,i]=np.std(ADC[:,(i*sliding):((i+1)*sliding)],axis=1)
    try:
        start_window = np.argmin(aux,axis=1)*sliding
    except ValueError:
        print_colored("ERROR: There is a problem with the pedestal computation. Check the data!", "ERROR")
        start_window = np.zeros(nwvfs)
    
    ADC_s = shift_ADCs(ADC,(-1)*start_window)

    if debug: print_colored("Calculating pedestal variables from sliding window of %i bins"%(sliding), "INFO")
    return ADC_s, start_window

def compute_ana_wvfs(my_runs, debug = False):
    '''
    Computes the peaktime and amplitude of a collection of a run's collection in standard format
    '''
    # Import from other libraries
    from .io_functions import print_colored, print_keys

    for run,ch in product(np.array(my_runs["NRun"]).astype(int),np.array(my_runs["NChannel"]).astype(int)):
        my_runs[run][ch]["AnaADC"] = my_runs[run][ch]["RawPChannel"]*((my_runs[run][ch]["RawADC"].T-my_runs[run][ch]["RawPedMean"]).T)
        print_colored("Analysis wvfs have been computed for run %i ch %i"%(run,ch), "blue")
        if debug: print_keys(my_runs)
        

def compute_power_spec(ADC, timebin, debug = False):
    ''' 
    Computes the power spectrum of the given events. It returns both axis. 
    '''

    aux = [] 
    aux_X = np.fft.rfftfreq(len(ADC[0]), timebin)
    for i in range(len(ADC)): aux.append(np.fft.rfft(ADC[i]))

    return np.absolute(np.mean(aux, axis = 0)), np.absolute(aux_X)


@numba.njit
def shift_ADCs(ADC,shift,debug=False):
    ''' 
    Used for the sliding window. 
    '''

    N_wvfs=ADC.shape[0]
    aux_ADC=np.zeros(ADC.shape)
    for i in range(N_wvfs): aux_ADC[i]=shift4_numba(ADC[i],int(shift[i])) # Shift the wvfs
    print("ADCs have been shifted")
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

# def old_compute_pedestal_variables(my_runs, key = "", label = "", buffer = 200, debug = False):
#     '''
#     Computes the pedestal variables of a collection of a run's collection in standard format
#     **VARIABLES**:
#         - my_runs: dictionary containing the data
#         - key:     key of the variable to be used
#         - label:   label to be added to the variable name
#         - buffer:  number of samples to be used for the pedestal computation
#         - debug:   boolean to print debug messages
#     '''
#     key, label = get_ADC_key(my_runs, key, label, debug = debug)
#     for run,ch in product(my_runs["NRun"],my_runs["NChannel"]):
#         try:
#             # ped_lim = st.mode(my_runs[run][ch][label+"PeakTime"], keepdims=True)[0][0]-buffer # Deprecated function
#             values,counts = np.unique(my_runs[run][ch][label+"PeakTime"], return_counts=True)
#             ped_lim = values[np.argmax(counts)]-buffer
#             if ped_lim < 0: ped_lim = 200
#             my_runs[run][ch][label+"PedSTD"]  = np.std (my_runs[run][ch][key][:,:ped_lim],axis=1)
#             my_runs[run][ch][label+"PedMean"] = np.mean(my_runs[run][ch][key][:,:ped_lim],axis=1)
#             my_runs[run][ch][label+"PedMax"]  = np.max (my_runs[run][ch][key][:,:ped_lim],axis=1)
#             my_runs[run][ch][label+"PedMin"]  = np.min (my_runs[run][ch][key][:,:ped_lim],axis=1)
#             my_runs[run][ch][label+"PedLim"]  = ped_lim
#             # my_runs[run][ch][label+"PedRMS"]  = np.sqrt(np.mean(np.abs(my_runs[run][ch][key][:,:ped_lim]**2),axis=1))
#             print_colored("Pedestal variables have been computed for run %i ch %i"%(run,ch), "blue")
#         except KeyError: 
#             if debug: print_colored("*EXCEPTION: for %i, %i, %s pedestal variables could not be computed"%(run,ch,key), "WARNING")