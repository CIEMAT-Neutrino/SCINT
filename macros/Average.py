import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,delete_keys,save_proccesed_variables
from lib.wvf_functions import average_wvfs,integrate_wvfs

N_runs           = [10,22,26]     
N_runs_calib     = [2]     
N_channels       = [0,1,4,6]       
N_channels_calib = [0,1,6]       

DELETE_KEYS = ["Ana_ADC"]

RUNS       = load_npy(N_runs, N_channels,"Analysis_","../data/ana/")
RUNS_CALIB = load_npy(N_runs_calib, N_channels_calib,"Analysis_","../data/ana/") 

average_wvfs(RUNS)
average_wvfs(RUNS_CALIB)

integrate_wvfs(RUNS,"AVE_INT_LIMITS","AvWvf")
integrate_wvfs(RUNS_CALIB,"AVE_INT_LIMITS","AvWvf")

save_proccesed_variables(RUNS,"Analysis_","../data/ana/")
save_proccesed_variables(RUNS_CALIB,"Analysis_","../data/ana/")

delete_keys(RUNS,DELETE_KEYS)
delete_keys(RUNS_CALIB,DELETE_KEYS)

save_proccesed_variables(RUNS,"Average_","../data/ave/")
save_proccesed_variables(RUNS_CALIB,"Average_","../data/ave/")