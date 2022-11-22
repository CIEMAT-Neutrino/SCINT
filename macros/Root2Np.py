import sys
sys.path.insert(0, '../')

import numpy as np
from lib.io_functions import root2npy,read_input_file

input_file = input("Please select input File: ")
info = read_input_file(input_file)

RUNS = []; CH = []
RUNS = np.append(RUNS,info["CALIB_RUNS"])
RUNS = np.append(RUNS,info["LIGHT_RUNS"])
RUNS = np.append(RUNS,info["ALPHA_RUNS"])

CH = np.append(CH,info["CHAN_STNRD"])

root2npy(RUNS.astype(int),CH.astype(int))