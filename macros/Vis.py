# cd to /lib and run -> python3 Vis.py
import sys
sys.path.insert(0, '../')
from lib.vis_functions import vis_raw_npy

RUNS = [10]
CH   = [6]

OPT  = {"NORM":False,"LOGY":True,"BASELINE":True,"AVE":"AvWvf"}

vis_raw_npy(RUNS,CH,OPT) # Input variables should be lists of integers