# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')
from lib.vis_functions import vis_raw_npy

RUNS = [10,22,26]
CH   = [0,1,4,6]

OPT  = {"NORM":True,"LOGY":False,"BASELINE":True, "AVE":"AvWvf"}

vis_raw_npy(RUNS,CH,OPT) # Input variables should be lists of integers