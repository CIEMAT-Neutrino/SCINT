# ---------------------------------------------------------------------------------------------------------------------- #
#  =========================================== RUN:$ python3 02Process.py TEST ========================================= #
# This macro will use peak/pedestal variables (PRE-PROCESS) and save the ADC wvf with the new baseline/polarity ...      #
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

channels = np.append(channels,info["CHAN_TOTAL"])

# PROCESS WAVEFORMS (Run in loop to avoid memory issues)
for run, ch in product(runs.astype(int),channels.astype(int)):
    
    my_runs = load_npy([run],[ch],preset=str(info["LOAD_PRESET"][2]),info=info,compressed=True)
    compute_ana_wvfs(my_runs,debug=False)

    insert_variable(my_runs,np.ones(len(channels)),"PChannel") # Change polarity!
    compute_peak_variables(my_runs,key="ADC")                  # Compute new peak variables
    compute_pedestal_variables(my_runs,key="ADC",debug=False)  # Compute new ped variables
    
    # print_keys(my_runs)
    average_wvfs(my_runs,centering="NONE") # Compute average wvfs centering (choose from: "NONE", "PEAK", "THRESHOLD")

    delete_keys(my_runs,["RawADC",'RawPeakAmp', 'RawPeakTime', 'RawPedSTD', 'RawPedMean', 'RawPedMax', 'RawPedMin', 'RawPedLim','RawPChannel']) # Delete branches to avoid overwritting
    save_proccesed_variables(my_runs,preset=str(info["SAVE_PRESET"][2]),info=info, force=True) # Try preset ANA
    del my_runs
    gc.collect()