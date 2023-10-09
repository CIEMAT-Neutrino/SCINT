import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUONS_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"],"key":["ANA_KEY"]}
user_input = initialize_macro("03Integration",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])
### 03Integration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    ### Load
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][3], compressed=True, debug=user_input["debug"])    
    ### Compute
    integrate_wvfs(my_runs, info=info, key=user_input["key"][0], debug=user_input["debug"])
    ### Remove branches to exclude from saving
    # delete_keys(my_runs,[user_input["key"][0], "TimeStamp", "Sampling"])
    save_proccesed_variables(my_runs, preset=str(info["SAVE_PRESET"][3]),info=info, force=True, debug=user_input["debug"])
    ### Free memory
    del my_runs
    gc.collect()