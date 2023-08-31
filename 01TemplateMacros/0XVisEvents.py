import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0XVisEvents",["input_file","load_preset","key","runs","channels","cuts","debug"],default_dict={}, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT  = {
    "MICRO_SEC":   True,                 # Time in microseconds (True/False)
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "AveWvf",             # If computed, vis will show average (AveWvf,AveWvfSPE,etc.)
    "SHOW_PARAM":  True,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False),
    "CUTTED_WVF":  -1,                   # Shows all/un-cutted/cutted waveforms (True/False)
    "SAME_PLOT":   False,                # True if we want to plot different channels in the SAME plot
    "LEGEND":      False                 # Shows plot legend (True/False)
}

### 0XVisEvent
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int),preset=user_input["load_preset"][0],info=info,compressed=True) # preset could be RAW or ANA
label, my_runs = cut_selector(my_runs, user_input)
vis_npy(my_runs, user_input["key"],OPT=OPT) # Remember to change key accordingly (ADC or RawADC)