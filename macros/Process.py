import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy
from lib.io_functions import load_analysis_npy
from lib.ana_functions import compute_pedestal_variables
from lib.ana_functions import compute_peak_variables
from lib.ana_functions import insert_polarity
from lib.ana_functions import integrate
from lib.ana_functions import save_proccesed_variables
from lib.wvf_functions import average_wvfs

N_runs           = [10,22,26]     
N_runs_calib     = [2]     
N_channels       = [0,1,4,6]       
N_channels_calib = [0,1,6]       
Pl               = [-1,-1,-1,-1]   #polarity

# L_channels  =["SiPM1","SiPM2","PMT","SuperCell"]
RUNS=load_npy(N_runs, N_channels)
RUNS_CALIB = load_npy(N_runs_calib, N_channels_calib)
AVE_RUNS = load_npy(N_runs, N_channels)
AVE_RUNS_CALIB = load_npy(N_runs_calib, N_channels_calib)

# Customizable
PROP={}
PROP["sampling"]=4; #ns
PROP["NBins_Ped"]=400

# Run appropiate ana_functions
insert_polarity(RUNS,N_channels,Pl)
insert_polarity(RUNS_CALIB,N_channels_calib,Pl)
compute_pedestal_variables(RUNS,PROP["NBins_Ped"])
compute_pedestal_variables(RUNS_CALIB,PROP["NBins_Ped"])
compute_peak_variables(RUNS)
compute_peak_variables(RUNS_CALIB)

average_wvfs(AVE_RUNS)
average_wvfs(AVE_RUNS_CALIB)

integrate(RUNS,"BASELINE_INT_LIMITS")
integrate(RUNS_CALIB,"BASELINE_INT_LIMITS")
integrate(RUNS,"AVE_INT_LIMITS")
integrate(RUNS_CALIB,"AVE_INT_LIMITS")

# print(RUNS.keys())
save_proccesed_variables(RUNS)
save_proccesed_variables(RUNS_CALIB)

# ana_runs = load_analysis_npy(N_runs, N_channels)
# print(ana_runs[10][0]["Baseline_Int"])
