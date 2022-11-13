import sys
sys.path.insert(0, '../')

from lib.io_functions  import load_npy
from lib.ana_functions import compute_pedestal_variables,compute_peak_variables,compute_ana_wvfs,insert_variable,save_proccesed_variables

# Arrays used in load_run
N_runs           = [10,22,26]     
N_runs_calib     = [2]     
N_channels       = [0,1,4,6]       
N_channels_calib = [0,1,6]

# Missing variables to be inserted
POLARITY = [-1,-1,-1,-1]   #polarity
SAMPLING = [4e-9,4e-9,4e-9,4e-9]
LABELS   = ["SiPM","SiPM","PMT","SC"]

# Start load_run 
RUNS       = load_npy(N_runs, N_channels)
RUNS_CALIB = load_npy(N_runs_calib, N_channels_calib)

# Run appropiate ana_functions
insert_variable(RUNS,POLARITY,"P_channel")
insert_variable(RUNS_CALIB,POLARITY,"P_channel")

insert_variable(RUNS,SAMPLING,"Sampling")
insert_variable(RUNS_CALIB,SAMPLING,"Sampling")

insert_variable(RUNS,LABELS,"Label")
insert_variable(RUNS_CALIB,LABELS,"Label")

compute_peak_variables(RUNS)
compute_peak_variables(RUNS_CALIB)

compute_pedestal_variables(RUNS,PROP["NBins_Ped"])
compute_pedestal_variables(RUNS_CALIB,PROP["NBins_Ped"])

compute_ana_wvfs(RUNS)
compute_ana_wvfs(RUNS_CALIB)

# print(RUNS.keys())
# print(RUNS_CALIB.keys())
save_proccesed_variables(RUNS)
save_proccesed_variables(RUNS_CALIB)