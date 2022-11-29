import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
from itertools import product

from lib.io_functions import load_npy,save_proccesed_variables, read_input_file
from lib.wvf_functions import average_SPE_wvfs
from lib.cal_functions import calibrate

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

    calibrate(my_runs,int_key,OPT)

    average_SPE_wvfs(my_runs,ave_runs,int_key)
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")
    save_proccesed_variables(ave_runs,"Average_","../data/ave/")