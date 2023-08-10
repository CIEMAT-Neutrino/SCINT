import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("03Integration")
input_file = user_input["input_file"]
debug = user_input["debug"]
info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])
runs = np.append(runs,info["MUONS_RUNS"])

channels = np.append(channels,info["CHAN_TOTAL"])

for run, ch in product(runs.astype(int),channels.astype(int)):    
    my_runs = load_npy([run], [ch], preset=str(info["LOAD_PRESET"][3]), info=info, compressed=True, debug=debug)
    
    #### CUT SECTION ####
    # cut_min_max(my_runs, ["PedSTD"], {"PedSTD": [-1,7.5]})
    # cut_lin_rel(my_runs, ["PeakAmp","ChargeAveRange"])
    # cut_peak_finder(my_runs, ["ADC"], 2)
    #####################

    #### Align indivual waveforms + Average ####
    # average_wvfs(my_runs,centering="NONE") # Compute average wvfs VERY COMPUTER INTENSIVE!
    # average_wvfs(my_runs,centering="PEAK", label=str(info["ANA_LABEL"][0])) # Compute average wvfs VERY COMPUTER INTENSIVE!
    # average_wvfs(my_runs,centering="THRESHOLD") # Compute average wvfs EVEN MORE COMPUTER INTENSIVE!

    ## Charge Integration ##
    integrate_wvfs(my_runs, info = info, debug = debug) # Compute charge according to selected average wvf from input file ("AveWvf", "AveWvfPeak", "AveWvfThreshold")

    # delete_keys(my_runs,["GaussADC"]) # Delete branches to avoid overwritting
    save_proccesed_variables(my_runs, preset=str(info["SAVE_PRESET"][3]),info=info, force=True, debug=debug)
    del my_runs
    gc.collect()