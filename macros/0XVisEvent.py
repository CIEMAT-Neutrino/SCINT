# ---------------------------------------------------------------------------------------------------------------------- #
#  ========================================= RUN:$ python3 0XVisEvent.py 0 0,1,2 ======================================= #
# This macro will show the individual EVENTS of the introduced runs and channels to see if everything is working fine    #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../'); from lib import *; print_header()

##### INPUT RUNS AND OPTIONS #####
try:
    input_folder   = sys.argv[1]
    input_runs     = sys.argv[2]
    input_channels = sys.argv[3]
except IndexError:
    input_folder   = input("Please select FOLDER (e.g Feb22_2): ")
    input_runs     = input("Please select RUNS (separated with commas): ")
    input_channels = input("Please select CHANNELS (separated with commas): ")

runs     = [int(r) for r in input_runs.split(",")]
channels = [int(c) for c in input_channels.split(",")]

info = {"MONTH": [input_folder]}
OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "AveWvf",             # If computed, vis will show average (AveWvf,AveWvfSPE,etc.)
    "SHOW_PARAM":  False,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      False                 # Shows plot legend (True/False)
    }
###################################

##### LOAD RUNS #####
my_runs = load_npy(runs,channels,preset="RAW",info=info,compressed=True) # preset could be RAW or ANA
#####################

##### EVENT VISUALIZER #####
vis_npy(my_runs, ["RawADC"],-1,OPT=OPT) # Remember to change key accordingly (ADC or RawADC)
############################