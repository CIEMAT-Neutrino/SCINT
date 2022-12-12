# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import *

runs     = [99]
channels = [0]

OPT  = {
    "NORM":       False,                # Runs can be displayed normalised
    "LOGY":       False,                # Runs can be displayed in logy
    "SHOW_AVE":   "AveWvfThreshold",    # If computed, vis will show average
    "SHOW_PARAM": True,                 # Print terminal information
    "CHARGE_KEY": "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": True                 # Finds possible peaks in the window
    }

my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs
# my_runs = load_npy(runs,channels,"","../data/raw/") # Load processed wvfs
keys = ["AnaADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"
# keys = ["ADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"

generate_cut_array(my_runs)
cut_min_max(my_runs, ["PeakAmp"], {"PeakAmp": [0,25]})
vis_npy(my_runs,keys,OPT) # Input variables should be lists of integers

# vis_var_hist(my_runs,["PeakAmp"],[0.1,99.9])
#"PeakAmp","PeakTime","PedSTD","ChargeAveRange"

# vis_persistence(my_runs)