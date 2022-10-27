import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy
from lib.fit_functions import sipm_fit

N_runs     =[10]     
N_channels =[0,1]       

L_channels  =["SiPM1","SiPM2"]
RUNS = load_npy(N_runs, N_channels)

OPT = {"LOGY":False}

sipm_fit(RUNS,OPT)