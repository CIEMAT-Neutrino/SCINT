import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"runs":["CALIB_RUNS","LIGHT_RUNS","ALPHA_RUNS","MUONS_RUNS","NOISE_RUNS"],"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("02AnaProcess",["input_file","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

### 02Process
for run, ch in product(np.asarray(user_input["runs"]).astype(int),np.asarray(user_input["channels"]).astype(int)):
    my_runs = load_npy([run],[ch], info, preset=info["LOAD_PRESET"][2], compressed=True, debug=user_input["debug"])
    compute_ana_wvfs(my_runs,debug=False)
    delete_keys(my_runs,['RawADC','RawPeakAmp', 'RawPeakTime', 'RawPedSTD', 'RawPedMean', 'RawPedMax', 'RawPedMin', 'RawPedLim']) # Delete branches to avoid overwritting

    compute_peak_variables(my_runs, label="Ana", key="AnaADC", debug=user_input["debug"])     # Compute new peak variables
    compute_pedestal_variables(my_runs, label="Ana", key="AnaADC", debug=user_input["debug"]) # Compute new ped variables using sliding window

    save_proccesed_variables(my_runs,preset=str(info["SAVE_PRESET"][2]),info=info, force=True)
    del my_runs
    gc.collect()