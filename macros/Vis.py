# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')
from lib.vis_functions import vis_raw_npy

RUNS = [26]
CH   = [6]

OPT  = {
    "NORM":     False,
    "LOGY":     False,
    "BASELINE": False
    }

vis_raw_npy(RUNS,CH,OPT) # Input variables should be lists of integers