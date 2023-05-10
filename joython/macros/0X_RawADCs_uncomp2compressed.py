# Small script to convert RawADCs from uncompressed to compressed format (npy to npz)
# paralellized example: 
# cat RUN.txt | parallel --joblog out.txt -j10 "python3 03_Raw_Charges.py -r"

import sys,os
sys.path.insert(0, '../')
from lib import *

import argparse
DEBUG=False
if DEBUG:import faulthandler; faulthandler.enable();

# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("-r", "--Run", help = "Selected data taking",type=int)
# Read arguments from command line
args = parser.parse_args()
if args.Run is None : raise NotImplementedError("Must add run number with -r or --R")

# WEEK="APSAIA_VUV";
# WEEK="APSAIA_VIS";
WEEK="DAPHNE_VIS";
path="/scr/neutrinos/rodrigoa/"+WEEK+"/joython/"
Runs=open_runs_table("../macros/"+WEEK+".xlsx")
Runs=Runs[Runs["Run"]==int(args.Run)]


for run in Runs["Run"].array:
    Run_props=Runs.iloc[0]
    run_path=path+"run"+str(run).zfill(2)+"/";
    
    
    for ch in Run_props["Channels"]:
        ADC=open_run_var(run_path,"RawADC",[ch],compressed=False)
        ADC[ch]=ADC[ch].astype(np.uint16)
        save_run_var(ADC,run_path,"RawADC",compressed=True)
        
        del ADC
    os.system("rm "+run_path+"RawADC*.npy")