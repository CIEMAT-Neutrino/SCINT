import sys; sys.path.insert(0, '../'); from lib import *
user_input = initialize_macro("00Raw2Np")
input_file = user_input["input_file"]
debug = user_input["debug"]
info = read_input_file(input_file)

runs = []; channels = []
runs = np.append(runs,info["CALIB_RUNS"])
runs = np.append(runs,info["LIGHT_RUNS"])
runs = np.append(runs,info["ALPHA_RUNS"])
runs = np.append(runs,info["MUONS_RUNS"])
runs = np.append(runs,info["NOISE_RUNS"])

channels = np.append(channels,info["CHAN_TOTAL"])

# From the input txt file you can choose the extension of your input file
# DEPRECATED (PROBABLY :) )!
# if info["RAW_DATA"][0] == "ROOT":
#     print("----- Taking a .root file as input data -----")
#     root2npy(runs.astype(int),channels.astype(int),info=info)

if info["RAW_DATA"][0] == "DAT":
    print("----- Taking a .dat file as input data -----")
    binary2npy(runs.astype(int),channels.astype(int),info=info,compressed=True,force=True)