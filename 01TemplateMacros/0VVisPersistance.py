import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0VVisPersistance",["input_file","load_preset","variables","runs","channels","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT  = {
    "MICRO_SEC":   True,                 # Time in microseconds (True/False)
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False),
    "CUTTED_WVF":  -1,                   # Shows all/un-cutted/cutted waveforms (True/False)
    "SAME_PLOT":   False,                # True if we want to plot different channels in the SAME plot
    "LEGEND":      True,                 # Shows plot legend (True/False)
    "COMPARE":     "CHANNELS"            # Compare CHANNELS or RUNS
}

### 0VVisPersistance
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])
vis_persistence(my_runs)