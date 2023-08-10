import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("02Process")
input_file = user_input["input_file"]
debug = user_input["debug"]
info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])
runs = np.append(runs,info["MUONS_RUNS"])
runs = np.append(runs,info["NOISE_RUNS"])

channels = np.append(channels,info["CHAN_TOTAL"])

# PROCESS WAVEFORMS (Run in loop to avoid memory issues)
for run, ch in product(runs.astype(int),channels.astype(int)):
    
    my_runs = load_npy([run],[ch],preset=str(info["LOAD_PRESET"][2]),info=info,compressed=True)
    compute_ana_wvfs(my_runs,debug=False)

    insert_variable(my_runs,np.ones(len(channels)),"PChannel") # Change polarity!
    compute_peak_variables(my_runs,label=str(info["ANA_LABEL"][0]), key="ADC")  # Compute new peak variables
    # compute_pedestal_variables(my_runs,key="ADC", buffer = 150, debug=False)  # Compute new ped variables
    compute_pedestal_variables_sliding_window(my_runs, key="ADC", label=str(info["ANA_LABEL"][0]), debug = debug) # Compute new ped variables using sliding window

    average_wvfs(my_runs,label=str(info["ANA_LABEL"][0]), centering="PEAK") # Compute average wvfs centering (choose from: "NONE", "PEAK", "THRESHOLD")

    delete_keys(my_runs,["RawADC",'RawPeakAmp', 'RawPeakTime', 'RawPedSTD', 'RawPedMean', 'RawPedMax', 'RawPedMin', 'RawPedLim','RawPChannel']) # Delete branches to avoid overwritting
    save_proccesed_variables(my_runs,preset=str(info["SAVE_PRESET"][2]),info=info, force=True) # Try preset ANA
    del my_runs
    gc.collect()