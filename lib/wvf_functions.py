# import copy
import numpy as np
import my_functions
from itertools import product

def average_wvf(my_runs,PATH="data/ave/"):
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        print(run,ch)

        runs   = load_npy(run,ch,-1,"")
        try:
            ana_runs = load_analysis_npy(run,ch,-1,"")
            runs[run][ch]["ADC"] = 
            aux_path=PATH+"Average_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            np.save(aux_path,aux[run][ch])
            print("Saved data in:" , aux_path)
        except:
            print("EVENTS HAVE NOT BEEN PROCESSED! Please run Process.py")