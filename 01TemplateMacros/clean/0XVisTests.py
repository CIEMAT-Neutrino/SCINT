import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0XVisTests")
info = read_input_file(user_input["input_file"])

user_input = update_user_input(user_input, ["runs","channels","key"],debug=user_input["debug"])
runs     = [int(r) for r in user_input["runs"]]
channels = [int(c) for c in user_input["channels"]]

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "ALIGN":       False,
    "LOGY":        False,               # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "AveWvf",             # If computed, vis will show average (AveWvf,AveWvfSPE,etc.)
    "SHOW_PARAM":  False,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      True,                # Shows plot legend (True/False)
    "SHOW":        True,
    "CHARGEDICT":  False
    }
###################################

##### LOAD RUNS #####
# my_runs = load_npy(runs,channels,preset="RAW",info=info,compressed=True) # Load to visualize raw events
my_runs = load_npy(runs,channels,preset="ANA",info=info,compressed=True) # Load to visualize processed events
# my_runs = load_npy(runs, channels,preset="EVA",info=info,compressed=True) # Fast load (no ADC)
#####################
##### READ CHARGE DICTIONARY #####
# if OPT["CHARGEDICT"] == True:
#     for r in runs:
#         for c in channels:
#             dicti = np.load(info["PATH"][0]+info["MONTH"][0]+"/npy/run"+str(r).zfill(2)+"_ch"+str(c)+"/ChargeRangeDict.npz",allow_pickle=True, mmap_mode="w+")["arr_0"].item()
#             print("ChargeRanges for RUN", r, " and CHANNEL ",c, " :\n", dicti, "\n")

##### CUTS #####
cut_ped_std(my_runs, n_std = 2, chs_cut=channels, apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [60,650],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[0,1,3,4], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [1400,4500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [2500,7500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [5000,13300],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"], compare = "NONE", percentile=[0,100])
# cut_peak_finder(my_runs, ["ADC"], 2)

##### EVENT VISUALIZER #####
vis_npy(my_runs, user_input["key"], evt_sel = -1, same_plot = False, OPT = OPT) # Input variables should be lists of integers

##### VISUALIZE HISTOGRAMS #####
# vis_var_hist(my_runs, ["PeakTime"], compare = "NONE", percentile = [0,100],OPT = OPT, select_range=False)
# vis_var_hist(my_runs, ["ChargeAveRange","ChargeRange0"], compare = "CHANNELS", percentile = [0.1,99.9], OPT = OPT, select_range=False) 
# vis_two_var_hist(my_runs, ["PeakAmp", "ChargeAveRange"], compare = "CHANNELS", OPT = {"SHOW": True}, percentile=[0.1,99.9], select_range=False)

##### AVERAGE WAVEFORMS VISUALIZER #####
# vis_compare_wvf(my_runs, ["AveWvf"], compare = "CHANNELS", OPT = OPT) # Input variables should be lists of integers

######################
#### AVERAGE WAVEFORM MAKER ####
# average_wvfs(my_runs,centering="NONE",cut_label="Pruebasss") # Compute average wvfs VERY COMPUTER INTENSIVE!
# average_wvfs(my_runs,centering="PEAK") # Compute average wvfs VERY COMPUTER INTENSIVE!
# average_wvfs(my_runs,centering="THRESHOLD", threshold=60) # Compute average wvfs EVEN MORE COMPUTER INTENSIVE!
# save_proccesed_variables(my_runs,preset="EVA",info=info, force=True)
