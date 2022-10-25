import sys
sys.path.insert(0, '../')
from lib.my_functions import load_npy
from lib.wvf_functions import average_wvf

N_runs     =[10,22,26]     
N_channels =[0,1,4,6]       

L_channels  =["SiPM1","SiPM2","PMT","SuperCell"]
RUNS = load_npy(N_runs, N_channels)

average_wvf(RUNS)