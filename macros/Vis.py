# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import vis_npy, vis_var_hist

N_runs = [2]
N_channels  = [0,1]

OPT  = {
    "NORM":       False,            # Runs can be displayed normalised
    "LOGY":       False,            # Runs can be displayed in logy
    "SHOW_AVE":   "AvWvf",          # If computed, vis will show average
    "SHOW_PARAM": True,             # Print terminal information
    "CHARGE_KEY": "AVE_INT_LIMTS"   # Select charge info to be displayed. Default: "AVE_INT_LIMITS" (if computed)
    }

# RUN = load_npy(N_runs,N_channels) # Load default from raw
RUN = load_npy(N_runs,N_channels,"Analysis_","../data/ana/") # Load processed wvfs
KEYS = ["Ana_ADC"] # Choose between "ADC" or "Ana_ADC depending on wich run has been loaded"

vis_npy(RUN,KEYS,OPT) # Input variables should be lists of integers

# vis_var_hist(RUN,["AVE_INT_LIMITS"],1e-3)
#"Peak_amp","Peak_time","Ped_STD", "AVE_INT_LIMITS"