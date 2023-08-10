import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("04Calibration")
input_file = user_input["input_file"]
debug = user_input["debug"]
info = read_input_file(input_file)

runs = []
runs = np.append(runs,info["CALIB_RUNS"])

for key_label in ["channels"]:
    if check_key(user_input, key_label) == False:
        user_input[key_label]= input("Please select %s (separated with commas): "%key_label).split(",")
    else:
        if debug: print("Using %s from user input"%key_label)

channels = [int(c) for c in user_input["channels"]]
    

int_key = ["ChargeAveRange"]
OPT = {
    "LOGY":       True,
    "SHOW":       True,
    "THRESHOLD":  1,
    "WIDTH":      15,
    "PROMINENCE": 0.4,
    "ACCURACY":   1000
}

for run, ch in product(runs.astype(int),channels.astype(int)):
    my_runs = load_npy([run],[ch], preset=str(info["LOAD_PRESET"][4]), info=info,compressed=True)
    # my_runs = load_npy([run],[ch], preset = "CUTS", info=info, compressed=True)
    print_keys(my_runs)

    #### CUT SECTION ####
    # cut_min_max(my_runs, ["PedSTD"], {"PedSTD": [-1,7.5]})
    # cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"])
    # cut_peak_finder(my_runs, ["ADC"], 2)
    #####################


    ## Persistence Plot ##
    # vis_persistence(my_runs)
    #####################


    ## Calibration ##
    print("Run ", run, "Channel ", ch)

    popt, pcov, perr = calibrate(my_runs,[info["ANA_LABEL"][0]+int_key[0]],OPT, debug=debug)
    # Calibration parameters = mu,height,sigma,gain,sn0,sn1,sn2 ##
    calibration_txt(run, ch, popt, pcov, filename=info["ANA_LABEL"][0]+"gain", info=info, debug=debug)
    
    ## SPE Average Waveform ##
    if all(x !=-99 for x in popt):
        try:
            SPE_min_charge = popt[3]-abs(popt[5])
            print("SPE_min_charge: ",SPE_min_charge)
            SPE_max_charge = popt[3]+abs(popt[5])
            print("SPE_max_charge: ",SPE_max_charge)
            cut_min_max(my_runs, [info["ANA_LABEL"][0]+int_key[0]], limits = {info["ANA_LABEL"][0]+int_key[0]: [SPE_min_charge,SPE_max_charge]}, debug = debug)
            average_wvfs(my_runs, centering="NONE", key=info["ANA_LABEL"][0]+"ADC", label = info["ANA_LABEL"][0], cut_label="SPE", debug = debug)

            save_proccesed_variables(my_runs, info=info, branch_list=[info["ANA_LABEL"][0]+"AveWvfSPE"], force = True)
        
        except IndexError:
            print_colored("Fit did not converge, skipping SPE average waveform", color = "ERROR")
