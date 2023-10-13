import sys; sys.path.insert(0, '../'); from lib import *
user_input, info = initialize_macro("0WVisWvf",["input_file","load_preset","variables","runs","channels","debug"],default_dict={}, debug=True)
# info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])
OPT = opt_selector(debug=user_input["debug"])

### 0WVisWvf
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])
vis_compare_wvf(my_runs, user_input["variables"], OPT=OPT)