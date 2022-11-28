import matplotlib.pyplot as plt
import numpy as np
import uproot
import copy

from itertools import product

def check_key(OPT, key):
    try:
        OPT[key]
        return True    
    except KeyError:
        return False

def root2npy (runs, channels, in_path="../data/raw/", out_path="../data/raw/", info={}, debug=False):
    for run, ch in product (runs.astype(int),channels.astype(int)):
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file  = "run"+str(run).zfill(2)+"_ch"+str(ch)+".root"
        out_file = "run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
        
        """Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. \n Depends on uproot, awkward and numpy. \n Size increases x2 times. """
        try:
            f = uproot.open(in_path+in_file)
            my_dict = {}
            
            if debug:
                print("----------------------")
                print("Dumping file:", in_path+in_file)
            
            for branch in f["IR02"].keys():
                if debug: print("dumping brach:",branch)
                my_dict[branch]=f["IR02"][branch].array().to_numpy()
            
            # additional useful info
            my_dict["NBinsWvf"] = my_dict["ADC"][0].shape[0]
            my_dict["Sampling"] = info["SAMPLING"][0]
            my_dict["Label"] = info["CHAN_LABEL"][j]
            my_dict["PChannel"] = int(info["CHAN_POLAR"][j])

            np.save(out_path+out_file,my_dict)
            
            if debug:
                print(my_dict.keys())
                print("Saved data in:" , out_path+out_file)
                print("----------------------\n")

        except:
            print("--- File %s was not foud!!! \n"%in_file)

def load_npy(runs, channels, prefix = "", in_path = "../data/raw/", debug = False):
    """Structure: run_dict[runs][channels][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""
    my_runs = dict()
    my_runs["NRun"]     = runs
    my_runs["NChannel"] = channels
    
    for run in runs:
        aux = dict()
        for ch in channels:
            try:    
                try:
                    aux[ch] = np.load(in_path+prefix+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()           
                except:    
                    try:
                        aux[ch] = np.load("../data/ana/Analysis_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
                        if debug: print("Selected file does not exist, loading default analysis run")
                    except:
                        aux[ch] = np.load("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
                        if debug: print("Selected file does not exist, loading raw run")
                my_runs[run] = aux

                print("\nLoaded %sruns with keys:"%prefix)
                print(my_runs.keys())
                # print_keys(runs)

            except FileNotFoundError:
                print("\nRun", run, ", channels" ,ch," --> NOT LOADED (FileNotFound)")
    return my_runs

def print_keys(my_runs):
    try:
        for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
            print("----------------------")
            print("Dictionary keys --> ",list(my_runs[run][ch].keys()))
            print("----------------------\n")
    except:
        KeyError
        return print("Empty dictionary. No keys to print.")

def delete_keys(my_runs, keys):
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        try:
            del my_runs[run][ch][key]
        except KeyError:
            print("*EXCEPTION: ",run, ch, key," key combination is not found in my_runs")

def save_proccesed_variables(my_runs, prefix = "Analysis_", out_path = "../data/ana/", debug = False):
    """Does exactly what it says, no RawWvfs here"""
    # try:  
    aux = copy.deepcopy(my_runs) # Save a copy of my_runs with all modifications and remove the unwanted branches in the copy
    for run in aux["NRun"]:
        for ch in aux["NChannel"]:
            try:
                for key in aux[run][ch]["RawFileKeys"]:
                    del aux[run][ch][key]
            except:
                if debug: print("Original raw branches have already been deleted for run %i ch %i"%(run,ch))

            aux_path=out_path+prefix+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            np.save(aux_path,aux[run][ch])
            print("Saved data in:", aux_path)
    # except KeyError: 
    #     return print("Empty dictionary. Not saved.")

def read_input_file(input, path = "../input/", debug = False):
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

def copy_single_run(my_runs, runs, channels, keys):
    my_run = dict()
    my_run["NRun"] = []
    my_run["NChannel"] = []
    for run, ch, key in product(runs,channels,keys):
        try:
            my_run["NRun"].append(run)
            my_run["NChannel"].append(ch)
            my_run[run] = dict()
            my_run[run][ch] = dict()
            my_run[run][ch][key] = my_runs[run][ch][key]
        except KeyError:
            print(run,ch,key," key combination is not found in my_runs")
    return my_run
