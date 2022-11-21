# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import vis_npy, vis_var_hist


run = [1,2,3]
ch  = [0,1,6]

OPT  = {
    "NORM":     False,
    "LOGY":     False,
    "SHOW_AVE": "AvWvf",
    "SHOW_PARAM": True
    }

KEYS = ["Ana_ADC"]

RUN = load_npy(run,ch,"Analysis_","../data/ana/")

vis_npy(RUN,KEYS,OPT) # Input variables should be lists of integers

# vis_var_hist(RUN,["Ped_STD","AVE_INT_LIMITS"],1e-3)
#"Peak_amp","Peak_time","Ped_STD", AVE_INT_LIMITS