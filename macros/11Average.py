import sys; sys.path.insert(0, '../'); from lib import *
default_dict = {"channels":["CHAN_TOTAL"]}
user_input = initialize_macro("11Average",["input_file","runs","key","load_preset","save_preset","filter","debug"],default_dict=default_dict, debug=True)
info = read_input_file(user_input["input_file"][0], debug=user_input["debug"])

### 11Average
my_runs = load_npy(np.asarray(user_input["runs"]).astype(int), np.asarray(user_input["channels"]).astype(int), info, preset=user_input["load_preset"][0], compressed=True, debug=user_input["debug"])
compute_ana_wvfs(my_runs,info,debug=False)
delete_keys(my_runs,['RawADC','RawPeakAmp', 'RawPeakTime', 'RawPedSTD', 'RawPedMean', 'RawPedMax', 'RawPedMin', 'RawPedLim']) # Delete branches to avoid overwritting

label, my_runs = cut_selector(my_runs, user_input)
average_wvfs(my_runs, info, key=user_input["key"][0], label="Ana", cut_label="Noise", centering="NONE", debug=user_input["debug"])

save_proccesed_variables(my_runs, preset=user_input["save_preset"][0], info=info, force=True, debug=user_input["debug"])
del my_runs
gc.collect()