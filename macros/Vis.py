# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.ana_functions import *

from lib.vis_functions import*
from lib.cut_functions import*
from lib.fig_config import*

##### INPUT RUNS AND OPTIONS #####
# input_runs = input("Please select RUNS (separated with commas): ")
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

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "",          # If computed, vis will show average (AveWvf,SPEAveWvf,etc.)
    "SHOW_PARAM":  True,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      False                 # Shows plot legend (True/False)
    }
###################################

##### LOAD RUNS #####
my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs
# my_runs = load_npy(runs,channels,"Analysis_","../data/ana/") # Load processed wvfs

my_runs = load_npy(runs,channels,preset="ALL",info=info,compressed=True)

print(my_runs[runs[0]][channels[0]].keys())
get_units(my_runs)
generate_cut_array(my_runs)
#####################

##### CUTS #####
# cut_min_max(my_runs, ["PeakAmp"], {"PeakAmp": [18,1000]})
# cut_min_max_sim(my_runs, ["PeakAmp", "ChargeAveRange"], {"PeakAmp": [30,45], "ChargeAveRange": [1.2, 2]})
# cut_lin_rel(my_runs, ["PeakAmp", "ChargeAveRange"])
################

##### HISTOGRAMS #####
for r in runs:
    for c in channels:
        vis_var_hist(my_runs, r, c, "PeakAmp", [0.1,99.9], OPT = {"Show": True})
        vis_var_hist(my_runs, r, c, "ChargeAveRange",[0.1,99.9], {"Show": True})
        vis_two_var_hist(my_runs, r, c, ["PeakAmp", "ChargeAveRange"], OPT = {"Show": True})
######################

##### EVENT VISUALIZER #####
# vis_npy(my_runs, ["AnaADC"],OPT,-1) # Input variables should be lists of integers
############################