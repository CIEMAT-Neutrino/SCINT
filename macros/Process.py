import sys
sys.path.insert(0, '../')

from lib.my_functions import load_npy
from lib.my_functions import load_analysis_npy
from lib.ana_functions import compute_pedestal_variables
from lib.ana_functions import compute_peak_variables
from lib.ana_functions import insert_polarity
from lib.ana_functions import save_proccesed_variables

N_runs     =[10,22,26]     
N_channels =[0,1,4,6]       
Pl         =[-1,-1,-1,-1]   #polarity

L_channels  =["SiPM1","SiPM2","PMT","SuperCell"]
RUNS=load_npy(N_runs, N_channels)

# Customizable
PROP={}
PROP["sampling"]=4; #ns
PROP["NBins_Ped"]=400

# Run appropiate ana_functions
insert_polarity(RUNS,N_channels,Pl)
compute_pedestal_variables(RUNS,PROP["NBins_Ped"])
compute_peak_variables(RUNS)

# print(RUNS.keys())
save_proccesed_variables(RUNS)

ana_runs = load_analysis_npy(N_runs, N_channels)
# print(ana_runs[10][0]["P_channel"])
