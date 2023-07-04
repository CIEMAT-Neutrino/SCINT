# ---------------------------------------------------------------------------------------------------------------------- #
#  ============================== RUN:$ python3 05Scintillation.py TEST run channel ==================================== #
# This macro allow us to visualize average waveforms comparing ch or runs with vis_compare_wvf.                          #
# It also loads the "ChargeAveRange" computed in 02Process for the scintillation runs and plot the charge histogram      #
# The histogram is fitted to a Gaussian and the results can be stored in a txt in ../fit_data/filename_chX.txt           #
# TO DO --> plot histograms/fit same plot + Scintillation profiles with fits (tau_slow etc)                              #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../'); from lib import *; print_header()

try:
    input_file     = sys.argv[1]
    input_runs     = sys.argv[2]
    input_channels = sys.argv[3]
except IndexError:
    input_file     = input("Please select input file (e.g Feb22_2): ")
    input_runs     = input("Please select RUNS (separated with commas): ")
    input_channels = input("Please select CHANNELS (separated with commas): ")

info     = read_input_file(input_file)
runs     = [int(r) for r in input_runs.split(",")]
channels = [int(c) for c in input_channels.split(",")]

int_key = ["ChargeRange0"] #"ChargeAveRange"
OPT = {
    "LOGY": True,       # Runs can be displayed in logy (True/False)
    "NORM": True,       # Runs can be displayed normalised (True/False)
    "PRINT_KEYS":False,
    "MICRO_SEC":True,
    "SCINT_FIT":True,
    "LEGEND":False,     # Shows plot legend (True/False)
    "SHOW": True
    }


## Visualize average waveforms by runs/channels ##
# my_runs = load_npy(runs.astype(int),channels.astype(int),branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# my_runs = load_npy([25],[0],branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# vis_compare_wvf(my_runs, ["AveWvf"], compare="RUNS", OPT=OPT)
#################################################

    ### FITTING --> tau slow etc

# for run, ch in product(runs.astype(int),channels.astype(int)):
my_runs = load_npy(runs, channels,preset=str(info["LOAD_PRESET"][5]),info=info,compressed=True)
print_keys(my_runs)

## Integrated charge (scintillation runs) ##
# print("Run ", run, "Channel ", ch)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,4.5],"PeakAmp": [60,650],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[0,1,3,4], apply_all_chs=True)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,9],"PeakAmp": [1400,4500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
popt_ch = []; pcov_ch = []; perr_ch = []; popt_nevt = []; pcov_nevt = []; perr_nevt = []
popt, pcov, perr = charge_fit(my_runs, int_key, OPT); popt_ch.append(popt); pcov_ch.append(pcov); perr_ch.append(perr)
#################################################

# HAY QUE REVISAR ESTO
counter = 0
for run, ch in product (runs, channels):
    scintillation_txt(run, ch, popt[counter], pcov[counter], filename="pC", info=info) ## Charge parameters = mu,height,sigma,nevents ## 
    counter += 1
    ###JSON --> mapa runes (posibilidad)