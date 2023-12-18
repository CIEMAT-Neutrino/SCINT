import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS"],"channels":["CHAN_TOTAL"],"variables":["TYPE"]}
user_input, info = initialize_macro("04Calibration",["input_file","variables","filter","save","debug"],default_dict=default_dict, debug=True)
OPT = opt_selector(debug=user_input["debug"])
### 04Calibration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])

    label, my_runs = cut_selector(my_runs, user_input)
    popt, pcov, perr = calibrate(my_runs, info, [user_input["variables"][0]],OPT, debug=user_input["debug"])
    calibration_txt(run, ch, popt, pcov, filename="gain", info=info, save=user_input["save"], debug=user_input["debug"])