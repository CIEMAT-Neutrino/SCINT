# ---------------------------------------------------------------------------------------------------------------------- #
#  ========================================== RUN:$ python3 01PreProcess.py TEST ======================================= #
# This macro will process peak/pedestal variables (PRE-PROCESS) and save the AnaADC with the new baseline/polarity ...   #
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
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])
runs = np.append(runs,info["MUONS_RUNS"])

channels = np.append(channels,info["CHAN_STNRD"])

""" To-Do: Avoid using loop in this macro. Maybe "ADC" type dict can be loaded in lazy mode """

# PRE-PROCESS RAW #
for run, ch in product(runs.astype(int),channels.astype(int)):
    # Start to load_runs 
    my_runs = load_npy([run],[ch], preset="RAW", info=info, compressed=True)
    
    compute_peak_variables(my_runs,key="RawADC",label="Raw")
    compute_pedestal_variables(my_runs,key="RawADC",label="Raw")
    print_keys(my_runs)
    delete_keys(my_runs,["RawADC"]) # Delete previous peak and pedestal variables
    save_proccesed_variables(my_runs,"ALL",info=info, force=True)