# cd to /lib and run -> python3 Vis.py
from lib.vis_functions import vis_raw_npy

RUNS = [10]
CH   = [0,1,4,6]
POL  = [1,1,1,1]
PATH = "data/"

vis_raw_npy(RUNS,CH,POL,PATH) # Input variables should be lists of integers