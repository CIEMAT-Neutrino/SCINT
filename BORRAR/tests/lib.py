import uproot
import numpy as np

def load_larsoft_root(wvf_type,path,root_folder,debug=False):
    output = dict()
    if wvf_type == "RAW":
        output["PRETRIGGER"] = 100
        output["PEDESTAL"] = 1500
    
    elif wvf_type == "DEC":
        output["PRETRIGGER"] = 100
        output["PEDESTAL"] = 0
    
    else:
        output["PRETRIGGER"] = 0
        output["PEDESTAL"] = 0

    output["SAMPLING"] = 16e-9
    output["TRUE"] = dict()
    output["RECO"] = dict()
    
    raw = uproot.open(path)

    try:
        raw_ch = raw["opdigi"]["PhotonData"]["photon_opCh"].array().to_numpy()[0]
        raw_npe = raw["opdigi"]["PhotonData"]["photon_pulse"].array().to_numpy()[0]
        output["TRUE"]["CH"]  = raw_ch   
        output["TRUE"]["PE"]  = raw_npe
    except: 
        if debug: print("FILE DID NOT CONTAIN 'digispe' FOLDER")

    raw_wvf_list = raw[root_folder].keys()
    raw_wvfs        = []
    raw_wvfs_x      = []
    raw_event       = []
    raw_wvf_ch      = []
    raw_wvf_ch_num  = []
    raw_wvf_pe      = []

    for this_wvf in raw_wvf_list:
        if this_wvf == "TriggerData;1":
            continue
        else:
            wvf_info = this_wvf.split("_")
            wvf_info[5] = wvf_info[5].split(";")[0]
            raw_wvfs.append(raw[root_folder][this_wvf].to_numpy()[0])
            raw_wvfs_x.append(raw[root_folder][this_wvf].to_numpy()[1][:-1])
            raw_event.append(int(wvf_info[1]))
            raw_wvf_ch.append(int(wvf_info[3]))
            raw_wvf_ch_num.append(int(wvf_info[5]))
   
    output["RECO"]["EV"]   = np.asarray(raw_event)    
    output["RECO"]["CH"]   = np.asarray(raw_wvf_ch)                 
    output["RECO"]["#WVF"] = np.asarray(raw_wvf_ch_num)                 
    output["RECO"]["WVF"]    = raw_wvfs 
    output["RECO"]["WVF_X"]  = raw_wvfs_x 

    try:
        npy_wvfs   = np.asarray(raw_wvfs)
        npy_wvfs_x = np.asarray(raw_wvfs_x)   
        output["RECO"]["PE"]     = np.sum(   npy_wvfs,axis=1)  
        output["RECO"]["T0"]     = np.argmax(npy_wvfs,axis=1)     
        output["RECO"]["AMP"]    = np.max(   npy_wvfs,axis=1)      
        output["RECO"]["PED"]    = np.mean(  npy_wvfs[:,:output["PRETRIGGER"]]-output["PEDESTAL"],axis=1)      
        output["RECO"]["PEDSTD"] = np.std(   npy_wvfs[:,:output["PRETRIGGER"]]-output["PEDESTAL"],axis=1)
    
    except:
        photons_per_wvf = photon_arrival_times(output)
        for key in ["PE","AMP","T0","PED","PEDSTD"]:
            output["RECO"][key] = []
        for i in range(len(output["RECO"]["WVF"])):
            # print(len(photons_per_wvf[i]))
            output["RECO"]["PE"].append(len(photons_per_wvf[i]))
            output["RECO"]["T0"].append(photons_per_wvf[i])
            output["RECO"]["AMP"].append(np.max(raw_wvfs[i]))      
            output["RECO"]["PED"].append(np.mean(raw_wvfs[i][:output["PRETRIGGER"]])-output["PEDESTAL"])      
            output["RECO"]["PEDSTD"].append(np.std(raw_wvfs[i][:output["PRETRIGGER"]])-output["PEDESTAL"])      

        if debug: print("ARRAYS HAVE DIFFERENT SIZES")

    return output,["PE","AMP","T0","PED","PEDSTD","WVF","WVF_X"]

def photon_arrival_times(raw):
    photons_per_wvf = []

    for jj in range(len(raw["RECO"]["CH"])):
        min_wvf_time = np.min(raw["RECO"]["WVF_X"][jj])
        max_wvf_time = np.max(raw["RECO"]["WVF_X"][jj])
        photons_per_channel = raw["TRUE"]["PE"][np.where(raw["TRUE"]["CH"] == raw["RECO"]["CH"][jj])]
        photons_per_wvf.append(photons_per_channel[(photons_per_channel > min_wvf_time) & (photons_per_channel < max_wvf_time)])
    
    return photons_per_wvf

def order_wvfs(wvfs,key_list):
    output = dict()
    for ii in range(np.max(wvfs["RECO"]["EV"])):
        output[ii+1] = dict()
    
    for jj in range(len(wvfs["RECO"]["CH"])):
        output[wvfs["RECO"]["EV"][jj]][wvfs["RECO"]["CH"][jj]] = dict()
        for key in key_list:
            output[wvfs["RECO"]["EV"][jj]][wvfs["RECO"]["CH"][jj]][key] = []


    for kk in range(len(wvfs["RECO"]["WVF"])):
        for key in key_list:
            output[wvfs["RECO"]["EV"][kk]][wvfs["RECO"]["CH"][kk]][key].append(wvfs["RECO"][key][kk])
    
    return output