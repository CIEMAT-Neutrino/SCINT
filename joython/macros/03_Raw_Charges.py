import sys
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

WEEK="APSAIA_VUV";
# WEEK="APSAIA_VIS";
# WEEK="DAPHNE_VIS";
path="/scr/neutrinos/rodrigoa/"+WEEK+"/joython/"
Runs=open_runs_table("../macros/"+WEEK+".xlsx")
Runs=Runs[Runs["Run"]==int(args.Run)]


for run in Runs["Run"].array:
    Run_props=Runs.iloc[0]
    run_path=path+"run"+str(run).zfill(2)+"/";

    compress=False
    
    
    for ch in Run_props["Channels"]:
        ADC=open_run_var(run_path,"RawADC",[ch],compressed=compress)
        Pedestal_vars_SW=open_run_var(run_path,"Pedestal_vars",[ch],compressed=compress)
        
        ADC=do_run_things((ADC,Pedestal_vars_SW,Run_props["Polarity"]),substract_Pedestal)
        
        Charge_vars=do_run_things(ADC,compute_ChargeRange)
        save_run_var(Charge_vars,run_path,"Charge_vars",compressed=compress)
        
        del Pedestal_vars_SW, ADC

