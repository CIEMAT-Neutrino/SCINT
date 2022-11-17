# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import vis_npy, vis_var_hist


N_runs = [2,10,22]
N_channels  = [0,6]
KEYS = ["Ana_ADC"]

OPT  = {
    "NORM":     False,
    "LOGY":     False,
    "SHOW_AVE": "AvWvf",
    "SHOW_PARAM": True
    }

RUN = load_npy(N_runs,N_channels,"Analysis_","../data/ana/")

vis_npy(RUN,KEYS,OPT) # Input variables should be lists of integers
# vis_var_hist(RUN,["Ped_STD","AVE_INT_LIMITS"],1e-3)
#"Peak_amp","Peak_time","Ped_STD", AVE_INT_LIMITS
