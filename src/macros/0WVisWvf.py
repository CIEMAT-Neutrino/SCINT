import sys; sys.path.insert(0, '../../'); from lib import *
user_input, info = initialize_macro("0WVisWvf", ["input_file","preset_load","variables","runs","channels","save","debug"], default_dict={}, debug=True)
OPT = opt_selector(debug=user_input["debug"])
### 0WVisWvf
my_runs = load_npy(np.asarray(user_input["runs"]).astype(str), np.asarray(user_input["channels"]).astype(str), info, preset=user_input["preset_load"][0], compressed=True, debug=user_input["debug"])
vis_compare_wvf(my_runs, info, user_input["variables"], OPT=OPT, save=user_input["save"], debug=user_input["debug"])