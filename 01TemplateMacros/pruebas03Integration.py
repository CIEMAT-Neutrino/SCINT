import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUON_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("03Integration",["input_file","key","cuts","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

### 02Integration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][3], compressed=True, debug=user_input["debug"])
    
    #### CUT SECTION ####
    # cut_min_max(my_runs, ["PedSTD"], {"PedSTD": [-1,7.5]]})
    # cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"])
    # cut_peak_finder(my_runs, ["ADC"], 2)
    #####################

    label = ""; ch2cut = user_input["cuts"]["ch2cut"]; apply = user_input["cuts"]["apply"]
    if user_input["cuts"]["cut_min_max"][0]: 
        label = "cut_min_max_"
        cut_min_max(my_runs, keys=[user_input["cuts"]["cut_min_max"][1]], limits={user_input["cuts"]["cut_min_max"][1]: user_input["cuts"]["cut_min_max"][2]}, chs_cut=[], apply_all_chs=False ,debug=user_input["debug"]);
    if user_input["cuts"]["cut_ped_std"][0]:
        label = "cut_ped_std_"
        cut_ped_std(my_runs, n_std=user_input["cuts"]["cut_ped_std"][1], chs_cut=[], apply_all_chs=False, debug=user_input["debug"]);
    if user_input["cuts"]["cut_lin_rel"][0]: 
        label = "cut_lin_rel_"
        cut_lin_rel(my_runs, user_input["cuts"]["cut_lin_rel"][1])
    if user_input["cuts"]["cut_peak_finder"][0]:
        print("Working on this cut...Change parameters in the macro")
        # label = "cut_peak_finder_"
        # cut_peak_finder(my_runs, user_input["cuts"]["cut_peak_finder"][1], user_input["cuts"]["cut_peak_finder"][2])
    if user_input["cuts"]["cut_min_max_sim"][0]:
        print("Working on this cut...Change parameters in the macro")
        # label = "cut_min_max_sim_"
        # cut_min_max_sim(my_runs, keys, limits, debug = False)


    #### Align indivual waveforms + Average ####
    average_wvfs(my_runs, key=user_input["key"][0], label=label, centering="PEAK", debug=user_input["debug"])

    ## Charge Integration ##
    integrate_wvfs(my_runs, info=info, debug=user_input["debug"])

    delete_keys(my_runs,user_input["key"])
    save_proccesed_variables(my_runs, preset=str(info["SAVE_PRESET"][3]),info=info, force=True, debug=user_input["debug"])
    del my_runs
    gc.collect()