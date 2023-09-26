import sys
sys.path.insert(0, '../')

import pandas as pd
from lib.first_data_process import save_Run_Bin2Np
from lib.io_functions import open_runs_table

DEBUG=True
if DEBUG:import faulthandler; faulthandler.enable();

import argparse

DEBUG=False
if DEBUG:import faulthandler; faulthandler.enable();

# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("-r", "--Run", help = "Selected data taking",type=int)
parser.add_argument("-w", "--Week", help = "Selected period",type=str)
# Read arguments from command line
args = parser.parse_args()
if args.Run is None: raise NotImplementedError("Must add run number with -r or --Run")
if args.Week is None: raise NotImplementedError("Must add week with -w or --Week")
WEEK=args.Week;
# WEEK="APSAIA_VIS"   # 1st  week 
# WEEK="APSAIA_VUV"   # 2nd  week 
# WEEK="DAPHNE_VIS"   # 3rd  week 
# WEEK="DAPHNE_VUV"   # 4th  week 
# WEEK="APSAIA_VUV_2" # 5th  week 

in_path ="/scr/neutrinos/rodrigoa/"+WEEK+"/"
out_path="/scr/neutrinos/rodrigoa/"+WEEK+"/joython/"
Runs=open_runs_table("../macros/"+WEEK+".xlsx")
Runs=Runs[Runs["Run"]==int(args.Run)]

## Fifth Week: Apsaia VUV 2

for run in Runs["Run"].array:

    Run_props=Runs[Runs["Run"]==run].iloc[0]
    save_Run_Bin2Np(Run_props["Run"],Run_props["Channels"],Compressed=True,in_path=in_path,out_path=out_path)
