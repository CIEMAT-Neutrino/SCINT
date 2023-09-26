import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0VVisPersistance",["input_file","load_preset","variables","runs","channels","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

OPT = opt_selector(debug=True)

### 0VVisPersistance
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])
vis_persistence(my_runs)