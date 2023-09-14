import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("11Average",["input_file","runs","key","load_preset","save_preset","cuts","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

### 11Average
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])

label, my_runs = cut_selector(my_runs, user_input)
average_wvfs(my_runs, key=user_input["key"][0], label="Ana", cut_label="Signal", centering="NONE", debug=user_input["debug"])

# delete_keys(my_runs,user_input["key"])
save_proccesed_variables(my_runs, preset=user_input["save_preset"][0], info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()