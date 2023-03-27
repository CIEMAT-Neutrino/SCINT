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
if args.Run is None: raise NotImplementedError("Must add run number with -r or --R")

WEEK="APSAIA_VUV";
path="/scr/neutrinos/rodrigoa/"+WEEK+"/joython/"
Runs=open_runs_table("../macros/"+WEEK+".xlsx")
Run_props=Runs[Runs["Run"]==int(args.Run)].iloc[0]
run_path=path+"run"+str(Run_props["Run"]).zfill(2)+"/";


if not Run_props["Type"]=="Visible": sys.exit()

compress=False

for ch in Run_props["Channels"]:
    ADC          =open_run_var(run_path,"RawADC"          ,[ch],compressed=compress)
    Pedestal_vars=open_run_var(run_path,"Pedestal_vars_SW",[ch],compressed=compress)
    Peak_vars    =open_run_var(run_path,"Peak_vars"       ,[ch],compressed=compress)
    
    ADC=do_run_things((ADC,Pedestal_vars,Run_props["Polarity"]),substract_Pedestal)
    Avg_wvf=do_run_things((ADC,Peak_vars),compute_AverageWaveforms)

    save_run_var(Avg_wvf,run_path,"Avg_wvf",compressed=compress)
    
    del Pedestal_vars, ADC