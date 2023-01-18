# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.ana_functions import *

from lib.vis_functions import*
from lib.cut_functions import*
from lib.fig_config import*

# input_runs = input("Please select RU NS (separated with commas): ")
# runs = [int(r) for r in input_runs.split(",")]

# input_channels = input("Please select CHANNELS (separated with commas): ")
# channels = [int(c) for c in input_channels.split(",")]

runs     = [2] # COmo la gente normal
channels = [0,1]

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised
    "LOGY":        False,                # Runs can be displayed in logy
    "SHOW_AVE":    "",    # If computed, vis will show average
    "SHOW_PARAM":  True,                 # Print terminal information
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                 # Finds possible peaks in the window
    "LEGEND":      True
    }

my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs

get_units(my_runs)
generate_cut_array(my_runs)

# my_runs = load_npy(runs,channels,"","../data/raw/") # Load processed wvfs
keys = ["AnaADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"
# keys = ["ADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"

# generate_cut_array(my_runs)
# cut_min_max(my_runs, ["PeakAmp"], {"PeakAmp": [600,10600]})
cut_lin_rel(my_runs, ["PeakAmp", "ChargeAveRange"])
# vis_npy(my_runs,keys,OPT,-1) # Input variables should be lists of integers

for run in runs:
    for ch in channels:
        vis_two_var_hist(my_runs,run,ch,["PeakAmp", "ChargeAveRange"])
# vis_var_hist(my_runs,["PeakAmp"],[0.1,99.9])
# vis_two_var_hist(my_runs, ["PeakAmp", "ChargeAveRange"])
# vis_var_hist(my_runs,["ChargeAveRange"],[0.1,99.9])
#"PeakAmp","PeakTime","PedSTD","ChargeAveRange"

# vis_persistence(my_runs)

### Aux for Cuts!
# cut_lin_rel(my_runs, ["PeakAmp", "ChargeAveRange"], [0,500], [-10,20])
