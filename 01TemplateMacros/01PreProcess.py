import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("01PreProcess")
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

""" To-Do: Avoid using loop in this macro. Maybe "ADC" type dict can be loaded in lazy mode """

# PRE-PROCESS RAW #
for run, ch in product(runs.astype(int),channels.astype(int)):
    # Start to load_runs 
    my_runs = load_npy([run],[ch], preset="RAW", info=info, compressed=True)
    
    # compute_pedestal_variables(my_runs,key="RawADC",label="Raw") # Using a fix window for pedestal
    compute_pedestal_variables_sliding_window(my_runs,key="RawADC",label="Raw", start = 0) # Checking the best window in the pretrigger
    compute_peak_variables(my_runs,key="RawADC",label="Raw")
    print_keys(my_runs)
    delete_keys(my_runs,["RawADC"]) # Delete previous peak and pedestal variables
    save_proccesed_variables(my_runs,"ALL",info=info, force=True)
    del my_runs
    gc.collect()
