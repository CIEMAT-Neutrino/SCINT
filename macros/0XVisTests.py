# ---------------------------------------------------------------------------------------------------------------------- #
#  ========================================= RUN:$ python3 0XVisTests.py 0 0,1,2 ======================================= #
# This macro will show the individual EVENTS of the introduced runs and channels to see if everything is working fine    #
# Ideally we want to work in /pnfs/ciemat.es/data/neutrinos/FOLDER and so we mount the folder in our computer with:      #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import sys; sys.path.insert(0, '../'); from lib import *; #print_header()
import plotly.offline as py

##### INPUT RUNS AND OPTIONS #####
try:
    input_file     = sys.argv[1]
    input_runs     = sys.argv[2]
    input_channels = sys.argv[3]
except IndexError:
    input_file     = input("Please select input file (e.g Feb22_2): ")
    input_runs     = input("Please select RUNS (separated with commas): ")
    input_channels = input("Please select CHANNELS (separated with commas): ")

info     = read_input_file(input_file)
# info     = [read_input_file(in_fi) for in_fi in input_file.split(",")]
runs     = [int(r) for r in input_runs.split(",")]
channels = [int(c) for c in input_channels.split(",")]

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "ALIGN":       False,
    "LOGY":        False,               # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "",             # If computed, vis will show average (AveWvf,AveWvfSPE,etc.)
    "SHOW_PARAM":  False,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      True,                # Shows plot legend (True/False)
    "SHOW":        True
    }
###################################

##### LOAD RUNS #####
# my_runs = load_npy(runs,channels,preset="RAW",info=info,compressed=True)
# my_runs = load_npy(runs,channels,preset="ANA",info=info,compressed=True)
my_runs = load_npy(runs, channels,preset="EVA",info=info,compressed=True) # Fast load (no ADC)

# my_runs_0 = load_npy([runs[0]],[channels[0]],preset="EVA",info=info[0],compressed=True) # Fast load (no ADC)
# my_runs_1 = load_npy([runs[1]],[channels[1]],preset="EVA",info=info[1],compressed=True) # Fast load (no ADC)

# def Merge(dict_1, dict_2):
	# result = dict_1 | dict_2
    # for key in ["NRun","NChannel"]:
    #     result[key] = dict_1[key] + dict_2[key]
	# return result


# my_runs = {**my_runs_0, **my_runs_1}
# for key in ["NRun","NChannel"]:
#     my_runs[key] = my_runs_0[key] + my_runs_1[key]
# my_runs = Merge(my_runs_0,my_runs_1)
# print(my_runs.keys())
# print(my_runs["NRun"])
# print(my_runs["NChannel"])
# print(my_runs[4][0].keys())

#####################
# for r in runs:
#     for c in channels:
#         dicti = np.load("/media/andres/2Gb/data/SBND_XA_PDE/SBND_XA_VUV_DAPHNE/npy/run"+str(r).zfill(2)+"_ch"+str(c)+"/ChargeRangeDict.npz",allow_pickle=True, mmap_mode="w+")["arr_0"].item()
        # dicti = np.load("/media/andres/2Gb/data/Jan22/npy/run"+str(r).zfill(2)+"_ch"+str(c)+"/ChargeRangeDict.npz",allow_pickle=True, mmap_mode="w+")["arr_0"].item()
        # print("ChargeRanges for RUN", r, " and CHANNEL ",c, " :\n",    dicti)
##### CUTS #####
# cut_min_max(my_runs, ["PedSTD"], {"PedSTD": [-1,9]})
# cut_min_max(my_runs, ["PeakAmp"], {"PeakAmp": [20,30]})
# cut_min_max(my_runs, ["ChargeAveRange"], {"ChargeAveRange": [0.1954707989004316,0.2821972209267536]})
# cut_min_max(my_runs, ["PeakTime"], {"PeakTime": [3.85e-6,3.87e-6]}, chs_cut=[1], apply_all_chs=True)
# # # cut_peak_finder(my_runs, ["ADC"], 2)
cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,4.5],"PeakAmp": [60,650],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[0,1,3,4], apply_all_chs=True)
cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,9],"PeakAmp": [1400,4500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,9],"PeakAmp": [2500,7500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,9],"PeakAmp": [5000,13300],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"], percentile=[0,100])
# cut_min_max(my_runs, ["RawFinalPedSTD"], {"RawFinalPedSTD": [4,4.5]}, chs_cut=[3], apply_all_chs=True)
##### EVENT VISUALIZER #####
# vis_npy(my_runs, ["RawADC"], evt_sel = 0, same_plot = False, OPT = OPT, debug=True) # Input variables should be lists of integers
# vis_npy(my_runs, ["ADC"], evt_sel = 0, same_plot = False, OPT = OPT) # Input variables should be lists of integers
# vis_npy(my_runs, ["GaussADC"], evt_sel = -1, same_plot = False, OPT = OPT) # Input variables should be lists of integers
# vis_compare_wvf(my_runs, ["AveWvf"], compare = "CHANNELS", OPT = OPT) # Input variables should be lists of integers

#################
# #### HISTOGRAMS #####
# vis_var_hist(my_runs, ["PeakTime"], compare = "CHANNELS", percentile = [0,100],OPT = OPT)
# vis_var_hist(my_runs, ["PedSTD"], compare = "RUNS", percentile = [0.1,99.9], OPT = OPT)
# vis_var_hist(my_runs, ["PeakAmp"], compare = "RUNS", percentile = [0.1,99.9], OPT = OPT, select_range=False)
vis_var_hist(my_runs, ["ChargeRange0","ChargeRange1","ChargeRange2","ChargeRange6","ChargeRange7"], compare = "RUNS", percentile = [0.1,99.9], OPT = OPT)
# vis_var_hist(my_runs, ["RawPedMean","RawFinalPedMean"], compare = "NONE", percentile = [0.1,99.9], OPT = OPT)
# vis_var_hist(my_runs, ["RawPedSTD","RawFinalPedSTD"], compare = "NONE", percentile = [0.1,99.9], OPT = OPT)
# vis_two_var_hist(my_runs, ["ChargeAveRange", "PeakAmp"], compare = "CHANNELS", OPT = {"SHOW": True}, percentile=[0,100], select_range=True)
######################
# average_wvfs(my_runs,centering="NONE",cut_label="Pruebasss") # Compute average wvfs VERY COMPUTER INTENSIVE!
# average_wvfs(my_runs,centering="PEAK") # Compute average wvfs VERY COMPUTER INTENSIVE!
# average_wvfs(my_runs,centering="THRESHOLD", threshold=60) # Compute average wvfs EVEN MORE COMPUTER INTENSIVE!
# save_proccesed_variables(my_runs,preset="EVA",info=info, force=True)
