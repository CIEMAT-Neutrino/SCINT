import sys; sys.path.insert(0, '../'); from lib import *
user_input, info = initialize_macro("12GenerateSER",["input_file","load_preset","save_preset","debug"],default_dict={}, debug=True)
### 12GenerateSER
raw_runs = np.asarray(info["ALPHA_RUNS"]).astype(int)
dec_runs = np.asarray(info["LIGHT_RUNS"]).astype(int)
ref_runs = np.asarray(info["CALIB_RUNS"]).astype(int)
ana_ch   = np.asarray(info["CHAN_TOTAL"]).astype(int)
### Load runs
my_runs = load_npy([7], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"])  # Select runs to be deconvolved (tipichaly alpha)     
light_runs = load_npy([20], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template (tipichaly light)    
single_runs = load_npy([19], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template scaling (tipichaly SPE)
generate_SER(my_runs, light_runs, single_runs, debug=user_input["debug"])
### Remove branches to exclude from saving
save_proccesed_variables(my_runs, preset=user_input["save_preset"][0], info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()