import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0YVisHist2D",["input_file","variables","runs","channels","filter","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"][0], debug=False)

OPT = opt_selector(debug=user_input["debug"])

### 0ZVisHist2D
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), preset="EVA",info=info,compressed=True) # preset could be RAW or ANA
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])
vis_two_var_hist(my_runs, user_input["variables"], OPT = OPT, percentile=[0.1,99.9], select_range=False)