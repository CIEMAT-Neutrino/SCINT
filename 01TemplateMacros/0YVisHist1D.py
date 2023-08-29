import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0YVisHist1D",["input_file","variables","runs","channels","cuts","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT  = {
    "NORM":        False,               # Runs can be displayed normalised (True/False)
    "LOGY":        True,                # Runs can be displayed in logy (True/False)
    "SHOW_PARAM":  False,               # Print terminal information (True/False)
    "LEGEND":      True,                # Shows plot legend (True/False)
    "SHOW":        True,
    "CHARGEDICT":  False
    }

### 0YVisHist1D
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int),preset="EVA",info=info,compressed=True) # preset could be RAW or ANA
label, my_runs = cut_selector(my_runs, user_input)
vis_var_hist(my_runs, user_input["variables"], compare = "CHANNELS", percentile = [0.1, 99.9],OPT = OPT, select_range=False)