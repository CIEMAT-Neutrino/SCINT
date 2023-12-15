import sys; sys.path.insert(0, '../'); from lib import *
user_input, info = initialize_macro("0VVisPersistance", ["input_file","preset_load","runs","channels","filter","debug"], default_dict={}, debug=True)
### 0VVisPersistance
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), info, preset=user_input["preset_load"][0], compressed=True, debug=user_input["debug"])
label, my_runs = cut_selector(my_runs, user_input)
vis_persistence(my_runs, info, save=user_input["save"], debug=user_input["debug"])