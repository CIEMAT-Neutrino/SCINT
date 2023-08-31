import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUON_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("00Raw2Np",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

### 10Ana2Root
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), preset="EVA", info=info, compressed=True) # preset could be RAW or ANA
npy2root(my_runs, debug=user_input["debug"])