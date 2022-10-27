import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy,load_average_npy
from lib.fit_functions import sipm_fit,scint_fit

N_runs     =[10]     
N_channels =[0,1]       

L_channels  =["SiPM1","SiPM2"]
RUNS = load_npy(N_runs, N_channels)
AVE_RUNS = load_average_npy(N_runs, N_channels)

OPT = {"LOGY":False,"AVE":"AvWvf"} # To evaluate average wvf instead of raw select the appropiate key in the OPT dict. Else, exclude "AVE" or write "AVE":False
# OPT = {"LOGY":True}
sipm_fit(AVE_RUNS,OPT)
# scint_fit(AVE_RUNS,OPT)