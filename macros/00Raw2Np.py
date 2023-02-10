# ---------------------------------------------------------------------------------------------------------------------- #                                                     #
#  ============================================ RUN:$ python3 00Raw2Np.py TEST ========================================= #
# This macro will convert RAW DATA into NPY (NPZ that are npy compressed) files                                          #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# Once this is done we will find in the following distribution:                                                          #
#   data/MONTH/raw/runXX      with the waveY.dat files and                                                               #
#   data/MONTH/npy/runXX_chYY with npz created. (npz_names=keys of the my_runs dict in the macros' workflow)             #
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

# From the input txt file you can choose the extension of your input file
# NEEDS UPDATE!
# if info["RAW_DATA"][0] == "ROOT":
#     print("----- Taking a .root file as input data -----")
#     root2npy(runs.astype(int),channels.astype(int),info=info)

if info["RAW_DATA"][0] == "DAT":
    print("----- Taking a .dat file as input data -----")
    binary2npy(runs.astype(int),channels.astype(int),info=info,compressed=True,force=False)