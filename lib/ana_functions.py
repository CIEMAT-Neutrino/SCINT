import numpy as np
import copy

def insert_polarity(my_runs,CHANNELS,POL,PATH="../data/raw/"):
    """Insert polarity values for each type of signal"""
    
    N_channels =CHANNELS       
    Pl         =POL  #polarity
    P_channels ={}

    for ch,pl in zip(N_channels,Pl):
        P_channels[ch]=pl

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["P_channel"] =P_channels[ch]

def compute_pedestal_variables(my_runs,nbins,PATH="../data/raw/"):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Ped_STD"] =np.std (my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_mean"]=np.mean(my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_max"] =np.max (my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_min"] =np.min (my_runs[run][ch]["ADC"][:,:nbins],axis=1)

def compute_peak_variables(my_runs,range1=0,range2=0,PATH="../data/raw/"):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Peak_amp" ] =np.max    (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)
            my_runs[run][ch]["Peak_time"] =np.argmax (my_runs[run][ch]["ADC"][:,:]*my_runs[run][ch]["P_channel"],axis=1)


def save_proccesed_variables(my_runs,out_path="../data/ana/"):
    """Does exactly what it says, no RawWvfs here"""
    
    #  Remove the unwanted branches in the copy
    aux=copy.deepcopy(my_runs)
    for run in aux["N_runs"]:
        for ch in aux["N_channels"]:
            for key in aux[run][ch]["Raw_file_keys"]:
                    del aux[run][ch][key]
    
    # Save the info in aux dict
    for run in aux["N_runs"]:
        for ch in aux["N_channels"]:
            aux_path=out_path+"Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            np.save(aux_path,aux[run][ch])
            print("Saved data in:", aux_path)
