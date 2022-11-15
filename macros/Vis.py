# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')

from lib.vis_functions import vis_npy

RUN = 26
CH  = 6

OPT  = {
    "NORM":     False,
    "LOGY":     False,
    "SHOW_AVE": "AvWvf",
    "SHOW_PARAM": True
    }

vis_npy(RUN,CH,"Ana_ADC",OPT) # Input variables should be lists of integers