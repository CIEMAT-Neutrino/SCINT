import sys; sys.path.insert(0, '../../'); from lib import *
default_dict = {"channels":["CHAN_TOTAL"]}
user_input, info = initialize_macro("11Average",["input_file","runs","preset_load","variables","filter","debug"],default_dict=default_dict, debug=True)
### 11Average
for run, ch, variable in product(np.asarray(user_input["runs"]).astype(str),np.asarray(user_input["channels"]).astype(str), user_input["variables"]):
### Load
    my_runs = load_npy([run], [ch], info, preset=user_input["preset_load"][0], compressed=True, debug=user_input["debug"])
    ### Process
    if user_input["preset_load"][0] == "ANA":
        if check_key(my_runs[my_runs["NRun"][0]][my_runs["NChannel"][0]],"AnaADC") == False:
            if not compute_ana_wvfs(my_runs, info=info, debug=user_input["debug"]): continue
        delete_keys(my_runs,['RawADC','RawPeakAmp','RawPeakTime','RawPedSTD','RawPedMean','RawPedMax','RawPedMin','RawPedLim'])
    
    ### Check if the run is empty
    key, label = get_wvf_label(my_runs, "", "", debug=user_input["debug"])
    if key == "" and label == "": pass
    ### Compute
    branch_list = []
    user_input["filter"]["cut_df"][0] = True
    for ref in ["Noise","SPE"]:
        user_input["filter"]["cut_df"][1] = [[[ch],variable,"between",(float(my_runs[run][ch][f"AnaMinCharge{ref}"]),float(my_runs[run][ch][f"AnaMaxCharge{ref}"])),False]]
        cut_label, my_runs = cut_selector(my_runs, user_input)
        average_wvfs(my_runs, info, key=key, label=label, cut_label=ref, centering="NONE", debug=user_input["debug"])
        compute_peak_variables(my_runs, info=info, key=f"AnaAveWvf{ref}", label=f"AnaAve{ref}", debug=user_input["debug"])
        branch_list.append(f"AnaAveWvf{ref}")
        branch_list.append(f"AnaAve{ref}PeakAmp")
        branch_list.append(f"AnaAve{ref}PeakTime")
    # my_runs[run][ch][f"AnaAveWvfClean"] = my_runs[run][ch][f"AnaAveWvfSPE"] - my_runs[run][ch][f"AnaAveWvfNoise"]
    # branch_list.append(f"AnaAveWvfClean")
    ### Remove branches to exclude from saving
    save_proccesed_variables(my_runs, preset=None, branch_list=branch_list, info=info, force=True, debug=user_input["debug"])
    del my_runs
    gc.collect()