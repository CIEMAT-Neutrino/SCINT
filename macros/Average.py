import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy
from lib.wvf_functions import average_wvfs

N_runs           = [10,22,26]     
N_runs_calib     = [2]     
N_channels       = [0,1,4,6]       
N_channels_calib = [0,1,6]       

RUNS       = load_npy(N_runs, N_channels)
RUNS_CALIB = load_npy(N_runs_calib, N_channels_calib) 

# average_wvfs(RUNS)
# average_wvfs(RUNS_CALIB)

# integrate(RUNS,"BASELINE_INT_LIMITS")
# integrate(RUNS_CALIB,"BASELINE_INT_LIMITS")
# integrate(RUNS,"AVE_INT_LIMITS")
# integrate(RUNS_CALIB,"AVE_INT_LIMITS")