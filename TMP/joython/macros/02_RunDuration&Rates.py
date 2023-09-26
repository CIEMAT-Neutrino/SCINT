import sys
sys.path.insert(0, '../')

from lib.io_functions  import open_run_var,open_runs_table,do_run_things,save_run_var
from lib.ped_functions import compute_Pedestal,substract_Pedestal, compute_Peak
import argparse

# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("-w", "--Week", help = "Selected period",type=str)
# Read arguments from command line
args = parser.parse_args()
if args.Week is None: raise NotImplementedError("Must add week with -w or --Week")
WEEK=args.Week;

path="/scr/neutrinos/rodrigoa/"+WEEK+"/joython/"
Runs=open_runs_table("../macros/"+WEEK+".xlsx")

for run in Runs["Run"].array:

    Run_props=Runs[Runs["Run"]==run].iloc[0]
    run_path=path+"run"+str(run).zfill(2)+"/";

    compress=False

    for ch in [Run_props["Channels"][0]]:
        TS=open_run_var(run_path,"Timestamp",[ Run_props["Channels"][0] ],compressed=compress)

        duration=(TS[Run_props["Channels"][0]][-1]-TS[Run_props["Channels"][0]][0])
        Nev=TS[Run_props["Channels"][0]].shape[0]
        print(Nev,duration,Nev/duration)
        

