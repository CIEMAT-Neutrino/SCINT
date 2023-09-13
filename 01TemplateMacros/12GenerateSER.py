import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("11GenerateSER",["input_file","load_preset","save_preset","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

### 12GenerateSER
# my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])

raw_runs = np.asarray(info["ALPHA_RUNS"]).astype(int)
dec_runs = np.asarray(info["LIGHT_RUNS"]).astype(int)
ref_runs = np.asarray(info["CALIB_RUNS"]).astype(int)
# noi_runs = np.asarray(info["NOISE_RUNS"]).astype(int)
ana_ch   = np.asarray(info["CHAN_TOTAL"]).astype(int)

my_runs = load_npy([7], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"])  # Select runs to be deconvolved (tipichaly alpha)     
light_runs = load_npy([20], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template (tipichaly light)    
single_runs = load_npy([19], [0,1], preset=user_input["load_preset"][0], info=info, compressed=True, debug=user_input["debug"]) # Select runs to serve as dec template scaling (tipichaly SPE)

# keys = ["AveWvf","SER","AveWvf"] # keys contains the 3 labels required for deconvolution keys[0] = raw, keys[1] = det_response and keys[2] = deconvolution 
# Entrada, deconvolucion, salida. That is: alpha wvf, SPE - Laser result (see in generate_SER to select type of wvf), name for dec wvf (Gauss + str) 
generate_SER(my_runs, light_runs, single_runs, debug=user_input["debug"])

# label, my_runs = cut_selector(my_runs, user_input)
# average_wvfs(my_runs, key=user_input["key"][0], label="Ana", cut_label="Signal", centering="NONE", debug=user_input["debug"])

# # delete_keys(my_runs,user_input["key"])
save_proccesed_variables(my_runs, preset=user_input["save_preset"][0], info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()