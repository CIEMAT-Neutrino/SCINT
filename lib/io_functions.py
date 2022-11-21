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

def root2npy (RUNS,CHANNELS,in_path="../data/raw/",out_path="../data/raw/"):
    for run, ch in product (RUNS,CHANNELS):
        in_file  = "run"+str(run).zfill(2)+"_ch"+str(ch)+".root"
        out_file = "run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
        DEBUG=False
        """Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. \n Depends on uproot, awkward and numpy. \n Size increases x2 times. """
        try:
            f = uproot.open(in_path+in_file)
            my_dict={}
            print("----------------------")
            print("Dumping file:", in_path+in_file)
            for branch in f["IR02"].keys():
                if DEBUG: print("dumping brach:",branch)
                my_dict[branch]=f["IR02"][branch].array().to_numpy()
            
            #additional useful info
            my_dict["NBins_wvf"]=my_dict["ADC"][0].shape[0]
            my_dict["Raw_file_keys"]=f["IR02"].keys()
            my_dict["Raw_file_keys"].remove("Sampling")
            my_dict["Raw_file_keys"].remove("ADC")

            print(my_dict.keys())
            np.save(out_path+out_file,my_dict)
            print("Saved data in:" , out_path+out_file)
            print("----------------------\n")

        except:
            print("--- File %s was not foud!!! \n"%in_file)

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

def read_input_file(input,PATH="../input/"):
    # Using readlines()
    file = open(PATH+input, 'r')
    lines = file.readlines()
    info = dict()
    RUNS = ["MUONS_RUNS","LIGHT_RUNS","ALPHA_RUNS","CALIB_RUNS"]
    # Strips the newline character
    for line in lines:
        if line.startswith("MONTH"):
            info["MONTH"] = line.strip(" ")[1]
        for RUN in RUNS:
            if line.startswith(RUN):
                info[RUN] = []
                for i in range(len(line.strip(" ")[1])):
                    info[RUN].append(line.strip(" ")[1].strip(",")[i])
                    print(line.strip(""))
        # print("Line{}: {}".format(count, line.strip()))
    print(info["CALIB_RUNS"])