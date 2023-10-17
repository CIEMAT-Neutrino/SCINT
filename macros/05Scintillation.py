import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["ALPHA_RUNS"],"channels":["CHAN_TOTAL"],"variables":["TYPE"]}
user_input, info = initialize_macro("05Calibration",["input_file","load_preset","key","filter","debug"],default_dict=default_dict, debug=True)
OPT = opt_selector(debug=user_input["debug"])
### 05Calibration
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int), info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])
popt_ch = []; pcov_ch = []; perr_ch = []; popt_nevt = []; pcov_nevt = []; perr_nevt = []
label, my_runs = cut_selector(my_runs, user_input)
popt, pcov, perr = charge_fit(my_runs, [user_input["key"][0].split("ADC")[0]+user_input["variables"][0]], OPT); popt_ch.append(popt); pcov_ch.append(pcov); perr_ch.append(perr)

# HAY QUE REVISAR ESTO
counter = 0
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    scintillation_txt(run, ch, popt[counter], pcov[counter], filename="pC", info=info) ## Charge parameters = mu,height,sigma,nevents ## 
    counter += 1
    ###JSON --> mapa runes (posibilidad)