import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUONS_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"],"key":["ANA_KEY"]}
user_input = initialize_macro("03Integration",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

### 03Integration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][3], compressed=True, debug=user_input["debug"])
    
    average_wvfs(my_runs, key=user_input["key"][0], centering="NONE", debug=user_input["debug"])
    integrate_wvfs(my_runs, info=info, key=user_input["key"][0], debug=user_input["debug"])

    delete_keys(my_runs,user_input["key"])
    save_proccesed_variables(my_runs, preset=str(info["SAVE_PRESET"][3]),info=info, force=True, debug=user_input["debug"])
    del my_runs
    gc.collect()