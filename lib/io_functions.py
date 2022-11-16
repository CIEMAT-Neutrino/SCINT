import matplotlib.pyplot as plt
import numpy as np
import uproot
import copy

from itertools import product

def check_key(OPT,KEY):
    try:
        OPT[KEY]
        return True    
    except KeyError:
        return False

def root2npy (in_path,out_path):
    DEBUG=False
    """Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. \n Depends on uproot, awkward and numpy. \n Size increases x2 times. """

    f = uproot.open(in_path)
    my_dict={}
    print("----------------------")
    print("Dumping file:", in_path)
    for branch in f["IR02"].keys():
        if DEBUG: print("dumping brach:",branch)
        my_dict[branch]=f["IR02"][branch].array().to_numpy()
    
    #additional useful info
    my_dict["NBins_wvf"]=my_dict["ADC"][0].shape[0]
    my_dict["Raw_file_keys"]=f["IR02"].keys()
    my_dict["Raw_file_keys"].remove("Sampling")
    my_dict["Raw_file_keys"].remove("ADC")

    print(my_dict.keys())
    np.save(out_path,my_dict)
    print("Saved data in:" , out_path)

def load_npy(RUNS,CH,PREFIX = "",PATH = "../data/raw/"):
    """Structure: run_dict[RUN][CH][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

    runs = dict()
    runs["N_runs"]     = RUNS
    runs["N_channels"] = CH
    
    for run in RUNS:
        channels=dict()
        for ch in CH:
            try:
                channels[ch] = np.load(PATH+PREFIX+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
            
            except:    
                try:
                    channels[ch] = np.load("../data/ana/Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
                    # del channels[ch]["Ana_ADC"]
                    print("Selected file does not exist, loading default analysis run")
                
                except:
                    channels[ch] = np.load("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
                    # del channels[ch]["ADC"]
                    print("Selected file does not exist, loading raw run")

        runs[run]=channels
    
    print("\nLoaded %sruns with keys:"%PREFIX)
    print(runs.keys())
    return runs

def delete_keys(my_runs,KEYS):
    for run,ch,key in product(my_runs["N_runs"],my_runs["N_channels"],KEYS):
        del my_runs[run][ch][key]

def save_proccesed_variables(my_runs,PREFIX="Analysis_",PATH="../data/ana/"):
    """Does exactly what it says, no RawWvfs here"""
    
    # Save a copy of my_runs with all modifications and remove the unwanted branches in the copy
    aux=copy.deepcopy(my_runs)
    
    for run in aux["N_runs"]:
        for ch in aux["N_channels"]:
            try:
                for key in aux[run][ch]["Raw_file_keys"]:
                    del aux[run][ch][key]
            except:
                if PREFIX == "Analysis_": print("Original raw branches have already been deleted for run %i ch %i"%(run,ch))

            aux_path=PATH+PREFIX+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            np.save(aux_path,aux[run][ch])
            print("Saved data in:", aux_path)
            
# def load_analysis_npy(RUNS,CH,PATH = "../data/ana/"):
#     """Structure: run_dict[RUN][CH][BRANCH] 
#     \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

#     runs=dict()
#     runs["N_runs"]    = RUNS
#     runs["N_channels"]= CH
#     # runs["P_channels"]=POL
    
#     for run in RUNS:
#         channels=dict()
#         for ch in CH:
#             channels[ch]=np.load(PATH+"Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
#         runs[run]=channels
#     return runs

# def load_average_npy(RUNS,CH,PATH = "../data/ave/"):
#     """Structure: run_dict[RUN][CH][BRANCH] 
#     \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

#     runs=dict()
#     runs["N_runs"]    =RUNS
#     runs["N_channels"]=CH
#     # runs["P_channels"]=POL
    
#     for run in RUNS:
#         channels=dict()
#         for ch in CH:
#             channels[ch]=np.load(PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
#         runs[run]=channels
#     return runs

# def load_fit_npy(RUNS,CH,PATH = "../data/fit/"):
#     """Structure: run_dict[RUN][CH][BRANCH] 
#     \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

#     runs=dict()
#     runs["N_runs"]    =RUNS
#     runs["N_channels"]=CH
#     # runs["P_channels"]=POL
    
#     for run in RUNS:
#         channels=dict()
#         for ch in CH:
#             channels[ch]=np.load(PATH+"Fit_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
#         runs[run]=channels
#     return runs

# def load_deconvolution_npy(RUNS,CH,PATH = "../data/dec/"):
#     """Structure: run_dict[RUN][CH][BRANCH] 
#     \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

#     runs=dict()
#     runs["N_runs"]    =RUNS
#     runs["N_channels"]=CH
#     # runs["P_channels"]=POL
    
#     for run in RUNS:
#         channels=dict()
#         for ch in CH:
#             channels[ch]=np.load(PATH+"Deconvolution_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
#         runs[run]=channels
#     return runs

# def insert_variable(my_runs,KEYS,VAR,out_path="../data/ana/"):
#     aux=copy.deepcopy(my_runs)
#     for run in aux["N_runs"]:
#         for ch in aux["N_channels"]:
#             for key in KEYS:
#                 aux[run][ch][key] = VAR[run][ch][key]
#                 print("Added key %s to npy"%key)
            
#             if out_path == "../data/ana/":
#                 aux_path=out_path+"Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
#             elif out_path == "../data/ave/":
#                 aux_path=out_path+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
#             elif out_path == "../data/dec/":
#                 aux_path=out_path+"Deconvolution_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
#             elif out_path == "../data/fit/":
#                 aux_path=out_path+"Fit_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            
#             np.save(aux_path,aux[run][ch])
#             print("Saved data in:", aux_path)