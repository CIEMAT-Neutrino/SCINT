import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("0XVisEvent")
input_file = user_input["input_file"]
debug = user_input["debug"]
info = read_input_file(input_file)

for key_label in ["runs","channels"]:
    if check_key(user_input, key_label) == False:
        user_input[key_label]= input("Please select %s (separated with commas): "%key_label).split(",")
    else:
        if debug: print("Using %s from user input"%key_label)

runs     = [int(r) for r in user_input["runs"]]
channels = [int(c) for c in user_input["channels"]]

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
###################################

##### LOAD RUNS #####
my_runs = load_npy(runs,channels,preset="ANA",info=info,compressed=True) # preset could be RAW or ANA
#####################

##### EVENT VISUALIZER #####
vis_npy(my_runs, ["GaussADC"],-1,OPT=OPT) # Remember to change key accordingly (ADC or RawADC)
############################