import sys; sys.path.insert(0, '../'); from lib import *
user_input, info = initialize_macro("0YVisHist1D", ["input_file","variables","runs","channels","filter","save","debug"], default_dict={}, debug=True)
OPT = opt_selector(debug=user_input["debug"])
### 0YVisHist1D
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), preset="EVA", info=info, compressed=True, debug=user_input["debug"])
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])
vis_var_hist(my_runs, info, user_input["variables"], percentile = [1, 99], OPT = OPT, select_range=False, save=user_input["save"], debug=user_input["debug"])