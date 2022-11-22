import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
from itertools import product

from lib.io_functions import load_npy,save_proccesed_variables
from lib.wvf_functions import average_SPE_wvfs
from lib.cal_functions import calibrate

N_runs_calib     = [1,2,3]
N_channels_calib = [0,1,6]

for run, ch in product(N_runs_calib,N_channels_calib):
# RUNS = load_npy(N_runs_calib,N_channels_calib,"Analysis_","../data/ana/") #Funciona dando los arrays pero sigue un orden distinto
    RUNS = load_npy([run],[ch],"Analysis_","../data/ana/")
# AVE_RUNS = load_npy(N_runs_calib,N_channels_calib,"Average_","../data/ave/")
    AVE_RUNS = load_npy([run],[ch],"Average_","../data/ave/")
    INT_KEY = ["AVE_INT_LIMITS"]

    OPT = {
        "LOGY": True,
        "PRINT_KEYS":False
          }

    calibrate(RUNS,INT_KEY,OPT)

    # print(RUNS[2][1]["Sampling"])
    # print(RUNS[2][1]["Sampling"])

    average_SPE_wvfs(RUNS,AVE_RUNS,INT_KEY)
    save_proccesed_variables(RUNS,"Analysis_","../data/ana/")
    save_proccesed_variables(AVE_RUNS,"Average_","../data/ave/")

    # plt.plot(4e-9*np.arange(len(AVE_RUNS[2][6]["SPE_AvWvf"])),AVE_RUNS[2][6]["SPE_AvWvf"])
    # plt.show()