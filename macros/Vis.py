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

#Se pueden poner la primera entrada las runs y la segunda los canales para no cambiar la macro
if sys.argv[1]: input_runs = sys.argv[1]
else          : input_runs = input("Please select RUNS (separated with commas): ")

if sys.argv[2]: input_channels = sys.argv[2]
else          : input_channels = input("Please select CHANNELS (separated with commas): ")


input_file = input("Please select input File: ")
info = read_input_file(input_file)

runs     = [int(r) for r in input_runs.split(",")]
channels = [int(c) for c in input_channels.split(",")]

# runs     = [2] # COmo la gente normal
# channels = [0,1,6,6]

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "SPEAvWvf",          # If computed, vis will show average (AveWvf,SPEAveWvf,etc.)
    "SHOW_PARAM":  True,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      False                 # Shows plot legend (True/False)
    }

# my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs

my_runs = load_npy(runs,channels,preset="ALL",info=info,compressed=True)

print(my_runs[runs[0]][channels[0]].keys())
get_units(my_runs)
generate_cut_array(my_runs)

# my_runs = load_npy(runs,channels,"","../data/raw/") # Load processed wvfs
keys = ["AnaADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"
# keys = ["ADC"] # Choose between "ADC" or "AnaADC depending on wich run has been loaded"

# cut_min_max(my_runs, ["ChargeAveRange"], {"ChargeAveRange": [1,2]})
# cut_min_max(my_runs, ["ChargeAveRange"], {"ChargeAveRange": [1,2]})
# vis_var_hist(my_runs,["ChargeAveRange"],[0.1,99.9])
# cut_lin_rel(my_runs, ["PeakAmp", "ChargeAveRange"])
# vis_two_var_hist(my_runs,7,1, ["PeakAmp", "ChargeAveRange"])
# vis_var_hist(my_runs,["PeakAmp"],[0.1,99.9])
# cut_min_max(my_runs, ["ChargeAveRange"], {"ChargeAveRange": [1,2]})
# cut_min_max(my_runs, ["PeakAmp"], {"PeakAmp": [18,1000]})
# vis_two_var_hist(my_runs,2,6, ["PeakAmp", "ChargeAveRange"])
vis_npy(my_runs,keys,OPT,-1) # Input variables should be lists of integers

# for run in runs:
#     for ch in channels:
#         vis_two_var_hist(my_runs,run,ch,["PeakAmp", "ChargeAveRange"])
# vis_var_hist(my_runs,["PeakAmp"],[0.1,99.9])
# vis_two_var_hist(my_runs, ["PeakAmp", "ChargeAveRange"])
# vis_var_hist(my_runs,["ChargeAveRange"],[0.1,99.9])
#"PeakAmp","PeakTime","PedSTD","ChargeAveRange"

# input_file = input("Please select input File: ")
# info = read_input_file(input_file)

# runs = []; channels = []
# runs = np.append(runs,info["CALIB_RUNS"])
# channels = np.append(channels,info["CHAN_STNRD"]) 

# for run, ch in product(runs.astype(int),channels.astype(int)):
#       my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")
#       int_key = ["ChargeAveRange"]
#       generate_cut_array(my_runs)
#       get_units(my_runs)
#       print("Run ", run, "Channel ", ch)
#       vis_var_hist(my_runs,["PeakAmp"],[0.1,99.9])