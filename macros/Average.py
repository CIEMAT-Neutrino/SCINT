import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,delete_keys,save_proccesed_variables
from lib.wvf_functions import average_wvfs,integrate_wvfs
from itertools import product

input_file = input("Please select input File: ")
info = read_input_file(input_file)

RUNS = []; CH = []
RUNS = np.append(RUNS,info["CALIB_RUNS"])
RUNS = np.append(RUNS,info["LIGHT_RUNS"])
RUNS = np.append(RUNS,info["ALPHA_RUNS"])

CH = np.append(CH,info["CHAN_STNRD"])      

DELETE_KEYS = ["Ana_ADC"]

""" To-Do: Simple average has already been computed in Process.py here a more refined Average should be computed: e.g. SPE for CALIB RUNS... """

# PROCESS WAVEFORMS (Run in loop to avoid memory issues)
for run, ch in product(RUNS.astype(int),CH.astype(int)):
    # Start load_run 
    my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")

    integrate_wvfs(my_runs,["Range"],"AvWvf",["DAQ", 250],[0,100])
    
    delete_keys(my_runs,DELETE_KEYS)
    save_proccesed_variables(my_runs,"Average_","../data/ave/")