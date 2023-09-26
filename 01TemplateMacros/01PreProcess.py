import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUONS_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("01PreProcess",["input_file","key","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

### 01PreProcess
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][1], compressed=True, debug=user_input["debug"])
    
    compute_peak_variables(my_runs, key=user_input["key"][0], label="", debug=user_input["debug"])
    compute_pedestal_variables(my_runs, key=user_input["key"][0], label="", debug=user_input["debug"]) # Checking the best window in the pretrigger

    delete_keys(my_runs,[user_input["key"][0]]) # Delete previous peak and pedestal variables
    save_proccesed_variables(my_runs, info, preset=info["SAVE_PRESET"][1], force=True, debug=user_input["debug"])
    
    del my_runs
    gc.collect()
