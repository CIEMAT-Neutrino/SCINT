# cd to /lib and run -> python3 Vis.py
from lib.vis_functions import vis_raw_npy

PATH = "data/"

RUNS = [10]
CH   = [0,1,4,6]
POL  = [1,1,1,1]

# OPT  = [AdjBaseLine,Norm,LogY]
OPT  = [True,True,True]

vis_raw_npy(RUNS,CH,POL,OPT,PATH) # Input variables should be lists of integers