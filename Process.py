from lib.my_functions import load_npy
from lib.my_functions import compute_pedestal_variables
from lib.my_functions import compute_peak_variables

N_runs     =[10,22,26]     
N_channels =[0,1,4,6]       
Pl         =[-1,-1,-1,-1]   #polarity
P_channels ={}
for ch,pl in zip(N_channels,Pl): P_channels[ch]=pl

L_channels  =["SiPM1","SiPM2","PMT","SuperCell"]
RUNS=load_npy(N_runs, N_channels,P_channels,"data/")

#Customizable
PROP={};
PROP["sampling"]=4; #ns
PROP["NBins_Ped"]=250;

# RUNS.keys()

compute_pedestal_variables(RUNS,PROP["NBins_Ped"])
# RUNS["10"][0].keys()

compute_peak_variables(RUNS)
# RUNS["10"][0].keys()