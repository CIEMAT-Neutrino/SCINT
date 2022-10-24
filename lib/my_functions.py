import matplotlib.pyplot as plt
import numpy as np
import uproot

from pynput import keyboard
from itertools import product

def root2npy (in_path,out_path):
    DEBUG=False;
    """Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. \n Depends on uproot, awkward and numpy. \n Size increases x2 times. """
    # in_path ="../data/run26_ch6.root"
    # out_path="../data/run26_ch6.npy"
    f=uproot.open(in_path)
    my_dict={}
    print("----------------------")
    print("Dumping file:", in_path)
    for branch in f["IR02"].keys():
        if DEBUG: print("dumping brach:",branch)
        my_dict[branch]=f["IR02"][branch].array().to_numpy()
    
    #additional useful info
    my_dict["NBins_wvf"]=my_dict["ADC"][0].shape[0]
    my_dict["Raw_file_keys"]=f["IR02"].keys()

    print(my_dict.keys())
    np.save(out_path,my_dict)
    print("Saved data in:" , out_path)

def load_npy(RUNS,CH,POL,PATH = "../data/raw/"):
    """Structure: run_dict[RUN][CH][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

    runs=dict()
    runs["N_runs"]    =RUNS
    runs["N_channels"]=CH
    runs["P_channels"]=POL
    
    for run in RUNS:
        channels=dict()
        for ch in CH:
            channels[ch]=np.load(PATH+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
        runs[run]=channels
    return runs

def load_analysis_npy(RUNS,CH,POL,PATH = "../data/ana/"):
    """Structure: run_dict[RUN][CH][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

    runs=dict()
    runs["N_runs"]    =RUNS
    runs["N_channels"]=CH
    runs["P_channels"]=POL
    
    for run in RUNS:
        channels=dict()
        for ch in CH:
            channels[ch]=np.load(PATH+"Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
        runs[run]=channels
    return runs

def load_average_npy(RUNS,CH,POL,PATH = "../data/ave/"):
    """Structure: run_dict[RUN][CH][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

    runs=dict()
    runs["N_runs"]    =RUNS
    runs["N_channels"]=CH
    runs["P_channels"]=POL
    
    for run in RUNS:
        channels=dict()
        for ch in CH:
            channels[ch]=np.load(PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
        runs[run]=channels
    return runs
