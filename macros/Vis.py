# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')
from lib.vis_functions import vis_raw_npy

PATH = "data/"

RUNS = [10]
CH   = [0,1,4,6]
POL  = [-1,-1,-1,-1]

OPT  = {"NORM":True,"LOGY":False,"BASELINE":False}

vis_raw_npy(RUNS,CH,POL,OPT) # Input variables should be lists of integers