import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0YVisHist1D",["input_file","variables","runs","channels","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT  = {
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        True,               # Runs can be displayed in logy (True/False)
    "SHOW_PARAM":  False,                 # Print terminal information (True/False)
    "LEGEND":      True,                # Shows plot legend (True/False)
    "SHOW":        True,
    "CHARGEDICT":  False
    }

### 0YVisHist1D
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int),preset="EVA",info=info,compressed=True) # preset could be RAW or ANA

##### CUTS #####
label, my_runs = cut_selector(my_runs, user_input)

# cut_ped_std(my_runs, n_std = 2, chs_cut=channels, apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [60,650],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[0,1,3,4], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [1400,4500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [2500,7500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_min_max(my_runs, ["PeakAmp","PeakTime"], {"PeakAmp": [5000,13300],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
# cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"], compare = "NONE", percentile=[0,100])
# cut_peak_finder(my_runs, ["ADC"], 2)

##### VISUALIZE HISTOGRAMS #####
vis_var_hist(my_runs, user_input["variables"], compare = "NONE", percentile = [0.1, 99.9],OPT = OPT, select_range=False)
# vis_var_hist(my_runs, ["ChargeAveRange","ChargeRange0"], compare = "CHANNELS", percentile = [0.1,99.9], OPT = OPT, select_range=False) 
