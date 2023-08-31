import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS"],"channels":["CHAN_TOTAL"],"key":["ANA_KEY"],"variables":["TYPE"]}
user_input = initialize_macro("04Calibration",["input_file","variables","cuts","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"], debug=user_input["debug"])

OPT = {
    "LOGY":       True,
    "SHOW":       True,
    "THRESHOLD":  1,
    "WIDTH":      15,
    "PROMINENCE": 0.4,
    "COMPARE":    "NONE",
    "ACCURACY":   1000
}

### 04Calibration
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][4], compressed=True, debug=user_input["debug"])

    label, my_runs = cut_selector(my_runs, user_input)
    popt, pcov, perr = calibrate(my_runs,[user_input["key"][0].split("ADC")[0]+user_input["variables"][0]],OPT, debug=user_input["debug"])
    calibration_txt(run, ch, popt, pcov, filename=user_input["key"][0].split("ADC")[0]+"gain", info=info, debug=user_input["debug"])