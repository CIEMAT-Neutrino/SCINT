# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')
from lib.vis_functions import vis_raw_npy

PATH = "data/"

RUNS = [10]
CH   = [1]

OPT  = {"NORM":True,"LOGY":True,"BASELINE":True}

vis_raw_npy(RUNS,CH,OPT) # Input variables should be lists of integers