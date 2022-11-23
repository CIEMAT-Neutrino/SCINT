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

def root2npy (RUNS,CHANNELS,in_path="../data/raw/",out_path="../data/raw/",info={}):
    for run, ch in product (RUNS.astype(int),CHANNELS.astype(int)):
        i = np.where(RUNS==run)[0][0]
        j = np.where(CHANNELS==ch)[0][0]

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
            
            # additional useful info
            my_dict["NBins_wvf"]=my_dict["ADC"][0].shape[0]
            my_dict["Sampling"] = info["SAMPLING"][0]
            my_dict["Label"] = info["CHAN_LABEL"][j]
            my_dict["P_channel"] = info["CHAN_POLAR"][j]
            
            # prepare keys for remove
            # my_dict["Raw_file_keys"]=f["IR02"].keys()
            # my_dict["Raw_file_keys"].remove("Sampling")
            # my_dict["Raw_file_keys"].remove("ADC")

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
                    print("Selected file does not exist, loading default analysis run")
                
                except:
                    channels[ch] = np.load("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
                    print("Selected file does not exist, loading raw run")
        runs[run]=channels
    print("\nLoaded %sruns with keys:"%PREFIX)
    print(runs.keys())
    return runs

def delete_keys(my_runs,KEYS):
    for run,ch,key in product(my_runs["N_runs"].astype(int),my_runs["N_channels"].astype(int),KEYS):
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

def read_input_file(input,path="../input/",debug=False):
    # Using readlines()
    file = open(path+input+".txt", 'r')
    lines = file.readlines()
    info = dict()
    NUMBERS = ["MUONS_RUNS","LIGHT_RUNS","ALPHA_RUNS","CALIB_RUNS","CHAN_STNRD","CHAN_CALIB","CHAN_POLAR"]
    DOUBLES = ["SAMPLING"]
    STRINGS = ["OV_LABEL","CHAN_LABEL"]
    # Strips the newline character
    for line in lines:
        if line.startswith("MONTH"):
            info["MONTH"] = line.split(" ")[1]
        for LABEL in DOUBLES:
            if line.startswith(LABEL):
                info[LABEL] = []
                numbers = line.split(" ")[1]
                for i in numbers.split(","):
                    info[LABEL].append(float(i))
                    if debug: print(info[LABEL])
        for LABEL in NUMBERS:
            if line.startswith(LABEL):
                info[LABEL] = []
                numbers = line.split(" ")[1]
                for i in numbers.split(","):
                    info[LABEL].append(int(i))
                    if debug: print(info[LABEL])
        for LABEL in STRINGS:
            if line.startswith(LABEL):
                info[LABEL] = []
                numbers = line.split(" ")[1]
                for i in numbers.split(","):
                    info[LABEL].append(i)
                    if debug: print(info[LABEL])
    print(info.keys())
    return info

def copy_single_run(my_runs,RUN,CH,KEY):
    my_run = dict()
    my_run["N_runs"] = []
    my_run["N_channels"] = []
    for run, ch, key in product(RUN.astype(int),CH.astype(int),KEY):
        try:
            my_run["N_runs"].append(run)
            my_run["N_channels"].append(ch)
            my_run[run] = dict()
            my_run[run][ch] = dict()
            my_run[run][ch][key] = my_runs[run][ch][key]
        except:
            print(run,ch,key," combination is not found in my_runs")
    return my_run