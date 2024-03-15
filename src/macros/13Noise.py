import sys; sys.path.insert(0, '../../'); from lib import *
default_dict = {"channels":["CHAN_TOTAL"], "runs":["NOISE_RUNS"]}
user_input, info = initialize_macro("13Noise",["input_file","runs","key","preset_load","filter","debug"],default_dict=default_dict, debug=True)
### 13Noise
my_runs = load_npy(np.asarray(user_input["runs"]).astype(str), np.asarray(user_input["channels"]).astype(str), info, preset=user_input["preset_load"][0], compressed=True, debug=user_input["debug"])
compute_fft_wvfs(my_runs,info=info,key=user_input["key"][0],label=user_input["label"][0],debug=user_input["debug"])

save_proccesed_variables(my_runs, preset="FFT", info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()