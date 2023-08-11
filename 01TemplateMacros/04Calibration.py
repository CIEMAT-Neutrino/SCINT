import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS"],"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("04Calibration",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])
    
int_key = ["ChargeRangeFromPed0"]
OPT = {
    "LOGY":       True,
    "SHOW":       True,
    "THRESHOLD":  1,
    "WIDTH":      15,
    "PROMINENCE": 0.4,
    "ACCURACY":   1000
}

### 04Calibration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])

    #### CUT SECTION ####
    # cut_min_max(my_runs, ["PedSTD"], {"PedSTD": [-1,7.5]})
    # cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"])
    # cut_peak_finder(my_runs, ["ADC"], 2)
    #####################

    ## Persistence Plot ##
    # vis_persistence(my_runs)
    
    ## Calibration ##
    popt, pcov, perr = calibrate(my_runs,[info["ANA_LABEL"][0]+int_key[0]],OPT, debug=user_input["debug"])
    calibration_txt(run, ch, popt, pcov, filename=info["ANA_LABEL"][0]+"gain", info=info, debug=user_input["debug"])
    
    ## SPE Average Waveform ##
    if all(x !=-99 for x in popt):
        try:
            SPE_min_charge = popt[3]-abs(popt[5])
            print("SPE_min_charge: ",SPE_min_charge)
            SPE_max_charge = popt[3]+abs(popt[5])
            print("SPE_max_charge: ",SPE_max_charge)
            cut_min_max(my_runs, [info["ANA_LABEL"][0]+int_key[0]], limits = {info["ANA_LABEL"][0]+int_key[0]: [SPE_min_charge,SPE_max_charge]}, debug=user_input["debug"])
            average_wvfs(my_runs, centering="NONE", key=info["ANA_LABEL"][0]+"ADC", label = info["ANA_LABEL"][0], cut_label="SPE", debug=user_input["debug"])

            save_proccesed_variables(my_runs, info=info, branch_list=[info["ANA_LABEL"][0]+"AveWvfSPE"], force = True)
        
        except IndexError:
            print_colored("Fit did not converge, skipping SPE average waveform", color = "ERROR")
