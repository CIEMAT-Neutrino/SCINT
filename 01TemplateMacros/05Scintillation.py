import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["ALPHA_RUNS"],"channels":["CHAN_TOTAL"],"key":["ANA_KEY"],"variables":["TYPE"]}
user_input = initialize_macro("04Calibration",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

int_key = user_input["variables"]
OPT = {
    "LOGY": True,       # Runs can be displayed in logy (True/False)
    "NORM": True,       # Runs can be displayed normalised (True/False)
    "PRINT_KEYS":False,
    "MICRO_SEC":True,
    "SCINT_FIT":True,
    "LEGEND":False,     # Shows plot legend (True/False)
    "SHOW": True
    }


## Visualize average waveforms by runs/channels ##
# my_runs = load_npy(runs.astype(int),channels.astype(int),branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# my_runs = load_npy([25],[0],branch_list=["Label","Sampling","AveWvf"],info=info,compressed=True) #Remember to LOAD your wvf
# vis_compare_wvf(my_runs, ["AveWvf"], compare="RUNS", OPT=OPT)
#################################################

# for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])
print_keys(my_runs)

## Integrated charge (scintillation runs) ##
# print("Run ", run, "Channel ", ch)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,4.5],"PeakAmp": [60,650],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[0,1,3,4], apply_all_chs=True)
# cut_min_max(my_runs, ["PedSTD","PeakAmp","PeakTime"], {"PedSTD": [0,9],"PeakAmp": [1400,4500],"PeakTime": [3.7e-6,4e-6]}, chs_cut=[5], apply_all_chs=True)
popt_ch = []; pcov_ch = []; perr_ch = []; popt_nevt = []; pcov_nevt = []; perr_nevt = []
popt, pcov, perr = charge_fit(my_runs, [user_input["key"][0].split("ADC")[0]+int_key[0]], OPT); popt_ch.append(popt); pcov_ch.append(pcov); perr_ch.append(perr)
#################################################

# HAY QUE REVISAR ESTO
counter = 0
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    scintillation_txt(run, ch, popt[counter], pcov[counter], filename="pC", info=info) ## Charge parameters = mu,height,sigma,nevents ## 
    counter += 1
    ###JSON --> mapa runes (posibilidad)