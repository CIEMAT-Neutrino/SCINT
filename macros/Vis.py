# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import vis_npy, vis_var_hist

input_runs = input("Please select RUNS (separated with commas): ")
runs = [int(r) for r in input_runs.split(",")]

input_channels = input("Please select CHANNELS (separated with commas): ")
channels = [int(c) for c in input_channels.split(",")]

OPT  = {
        "NORM":       False,           # Runs can be displayed normalised
        "LOGY":       False,           # Runs can be displayed in logy
        "SHOW_AVE":   "AveWvf",        # If computed, vis will show average
        "SHOW_PARAM": True,            # Print terminal information
        "CHARGE_KEY": "ChargeAveRange" # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
       }

my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs
keys = ["AnaADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"

vis_npy(my_runs,keys,OPT) # Input variables should be lists of integers

# vis_var_hist(my_runs,["ChargeAveRange"],1e-3)
#"PeakAmp","PeakTime","PedSTD","ChargeAveRange"