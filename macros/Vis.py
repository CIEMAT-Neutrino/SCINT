# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.io_functions import *
from lib.vis_functions import vis_npy, vis_var_hist

run = [2]
ch  = [6]

OPT  = {
    "NORM":     False,
    "LOGY":     False,
    "SHOW_AVE": "AvWvf",
    "SHOW_PARAM": True
    }

RUN = load_npy(run,ch,"Analysis_","../data/ana/")

# vis_npy(RUN,CH,"Ana_ADC",OPT) # Input variables should be lists of integers
vis_var_hist(RUN,["AVE_INT_LIMITS"],5e-3)
# vis_var_hist(RUN,"Peak_time")
# vis_var_hist(RUN,"Ped_STD")
#"Peak_amp","Peak_time","Ped_STD",