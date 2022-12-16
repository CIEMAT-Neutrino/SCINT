import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
from itertools import product

from lib.io_functions import load_npy,save_proccesed_variables, read_input_file
from lib.wvf_functions import average_wvfs
from lib.cut_functions import *

input_file = input("Please select input File: ")
info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
channels = np.append(channels,info["CHAN_STNRD"])      

for run, ch in product(runs.astype(int),channels.astype(int)):
    my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")
    ave_runs = load_npy([run],[ch],"Average_","../data/ave/")
    int_key = ["ChargeAveRange"]

    OPT = {
        "LOGY": True,
        "PRINT_KEYS":False
          }

    min_value = dict()
    max_value = dict()
    min_value["ChargeAveRange"] = my_runs[run][ch]["MinChargeSPE"]
    max_value["ChargeAveRange"] = my_runs[run][ch]["MaxChargeSPE"]

    generate_cut_array(my_runs)
    cut_min_max(my_runs,["ChargeAveRange"],min_value,max_value)

    average_wvfs(my_runs)

    plt.plot(my_runs[run][ch]["Sampling"]*np.arange(len(my_runs[run][ch]["AveWvf"][0])),my_runs[run][ch]["AveWvf"][0])
    plt.show()