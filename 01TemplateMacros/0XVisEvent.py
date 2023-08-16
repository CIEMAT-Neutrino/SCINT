import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {}
user_input = initialize_macro("00Raw2Np",["input_file","load_preset","key","runs","channels","debug"],default_dict=default_dict, debug=True)

OPT  = {
    "MICRO_SEC":   True,
    "NORM":        False,                # Runs can be displayed normalised (True/False)
    "LOGY":        False,                # Runs can be displayed in logy (True/False)
    "SHOW_AVE":    "AveWvf",             # If computed, vis will show average (AveWvf,AveWvfSPE,etc.)
    "SHOW_PARAM":  True,                 # Print terminal information (True/False)
    "CHARGE_KEY":  "ChargeAveRange",     # Select charge info to be displayed. Default: "ChargeAveRange" (if computed)
    "PEAK_FINDER": False,                # Finds possible peaks in the window (True/False)
    "LEGEND":      False                 # Shows plot legend (True/False)
}

info = read_input_file(user_input["input_file"], debug=user_input["debug"])
my_runs = load_npy(user_input["runs"],user_input["channels"],preset=user_input["load_preset"][0],info=info,compressed=True) # preset could be RAW or ANA
vis_npy(my_runs, user_input["key"],-1,OPT=OPT) # Remember to change key accordingly (ADC or RawADC)