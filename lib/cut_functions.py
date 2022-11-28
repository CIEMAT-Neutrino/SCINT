import numpy as np

from itertools import product
from .io_functions import check_key,print_keys,copy_single_run

def generate_cut_array(my_runs):
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):    
        for key in my_runs[run][ch].keys():
            if key.find("ADC") > 0:
                ADC_key = key
                print(key)
        my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][ADC_key]),dtype=bool)

def cut_min_max(my_runs, keys, min, max):
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        if check_key(my_runs[run][ch], "MyCuts") == True:
            if check_key(my_runs[run][ch], key) == True:
                for i in range(len(my_runs[run][ch][key])):
                    if min[key] < my_runs[run][ch][key][i] < max[key]:
                       continue
                    else: my_runs[run][ch]["MyCuts"][i] = False
            else: print(key," does not exist in my_runs!")
        else: print("Run generate_cut_array")