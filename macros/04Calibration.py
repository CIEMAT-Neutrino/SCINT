# ---------------------------------------------------------------------------------------------------------------------- #
#  ========================================= RUN:$ python3 04Calibration.py TEST ======================================= #
# This macro will compute a CALIBRATION histogram where the peaks for the PED/1PE/2PE... are FITTED to obtain the GAIN   #
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
channels = np.append(channels,info["CHAN_TOTAL"])      

int_key = ["ChargeAveRange"]
OPT = {
    "LOGY": True,
    "SHOW": True
    }

for run, ch in product(runs.astype(int),channels.astype(int)):
    my_runs = load_npy([run],[ch], preset=str(info["LOAD_PRESET"][4]), info=info,compressed=True)#preset="ANA"
    # my_runs = load_npy([run],[ch], preset = "CUTS", info=info, compressed=True)
    
    print_keys(my_runs)
    #### APPLY CUTS ####
    # cut_min_max(my_runs, ["ChargeAveRange"], limits = {"ChargeAveRange": [-1,4]})
    # cut_min_max_sim(my_runs, ["ChargeAveRange"], limits = {"ChargeAveRange": [-1,4]})
    # cut_lin_rel(my_runs, ["PeakAmp", "ChargeAveRange"])
    ####################

    ## Persistence Plot ##
    # vis_persistence(my_runs)

    ## Calibration ##
    print("Run ", run, "Channel ", ch)
    popt, pcov, perr = calibrate(my_runs,int_key,OPT)
    # Calibration parameters = mu,height,sigma,gain,sn0,sn1,sn2 ##
    calibration_txt(run, ch, popt, pcov, filename="gain",info=info)
    
    ## SPE Average Waveform ##
    if all(x !=-99 for x in popt):
        SPE_min_charge = popt[3]-abs(popt[5])
        SPE_max_charge = popt[3]+abs(popt[5])
        cut_min_max(my_runs, int_key, limits = {int_key[0]: [SPE_min_charge,SPE_max_charge]})
        average_wvfs(my_runs,centering="NONE",cut_label="SPE")

        save_proccesed_variables(my_runs,info=info,branch_list=["AveWvfSPE"])
        # save_proccesed_variables(my_runs,info=info,preset="CUTS", force = True)