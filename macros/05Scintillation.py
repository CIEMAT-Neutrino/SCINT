# ---------------------------------------------------------------------------------------------------------------------- #
#  ======================================== RUN:$ python3 05Scintillation.py TEST ====================================== #
# This macro allow us to visualize average waveforms comparing ch or runs with vis_compare_wvf.                          #
# It also loads the "ChargeAveRange" computed in 02Process for the scintillation runs and plot the charge histogram      #
# The histogram is fitted to a Gaussian and the results can be stored in a txt in ../fit_data/filename_chX.txt           #
# TO DO --> plot histograms/fit same plot + Scintillation profiles with fits (tau_slow etc)                              #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../'); from lib import *; print_header()

try:
    input_file = sys.argv[1]
except IndexError:
    input_file = input("Please select input File: ")

info = read_input_file(input_file)
runs = []; channels = []
runs = np.append(runs,info["ALPHA_RUNS"])
# runs = np.append(runs,info["MUONS_RUNS"])

channels = np.append(channels,info["CHAN_STNRD"])

int_key = ["ChargeAveRange"]
OPT = {
    "LOGY": False,
    "NORM": True,
    "PRINT_KEYS":False,
    "MICRO_SEC":True,
    "SCINT_FIT":True,
    "LEGEND":True,
    "SHOW": True
    }

## Visualize average waveforms by runs/channels ##
# my_runs = load_npy(runs.astype(int),channels.astype(int),branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# my_runs = load_npy([25],[0],branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# vis_compare_wvf(my_runs, ["AveWvf"], compare="RUNS", OPT=OPT)
# FITTING --> tau slow etc Look fit_wvfs(my_runs,"SCINT",thrld,range,key,OPT)

for run, ch in product(runs.astype(int),channels.astype(int)):
    my_runs = load_npy([run],[ch], branch_list=["ADC","ChargeAveRange","AveWvf"], info=info,compressed=True) #preset="ANA"
    print_keys(my_runs)

    ## Integrated charge (scintillation runs) ##
    print("Run ", run, "Channel ", ch)
    popt, pcov, perr = charge_fit(my_runs,int_key,OPT)
    # scintillation_txt(run, ch, popt, pcov, filename="pC", info=info) ## Charge parameters = mu,height,sigma,nevents ## 
#     ### Repetir fits
#     #JSON --> mapa runes (posibilidad)