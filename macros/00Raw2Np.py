import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUONS_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input, info = initialize_macro("00Raw2Np",["input_file","debug"],default_dict=default_dict, debug=True)
### 00Raw2Np
binary2npy(np.asarray(user_input["runs"]).astype(str), np.asarray(user_input["channels"]).astype(str), info=info, compressed=True, force=True, debug=user_input["debug"])