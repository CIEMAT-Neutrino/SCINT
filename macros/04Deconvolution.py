import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from itertools import product

from lib.io_functions import load_npy,save_proccesed_variables
from lib.dec_functions import deconvolve

raw_runs = [25,26,27]
dec_runs = [9,10,11]
ref_runs = [1,2,3]

ana_ch =   [0,1,6]


for i in range(len(raw_runs)):
    my_runs     = load_npy([raw_runs[i]],ana_ch,"Average_",      "../data/ave/") # Activate in case deconvolution of average wvf wants to be performed
    light_runs  = load_npy([dec_runs[i]],ana_ch,"Average_",      "../data/ave/")
    single_runs = load_npy([ref_runs[i]],ana_ch,"Average_",      "../data/ave/")
    out_runs    = load_npy([raw_runs[i]],ana_ch,"Deconvolution_","../data/dec/")

    keys = ["AveWvf","AveWvf","DecADC"] # keys contains the 3 labels required for deconvolution keys[0] = raw, keys[1] = det_response and keys[2] = deconvolution 
    
    OPT = {
        # "KEY":"AnaADC", # Select key that correcponds to imported wvf runs (e.g. "AnaADC","AveWvf","SPEAveWvf"...)
        # "KEY":"SPEAveWvf", # Select key that correcponds to imported wvf runs (e.g. "AnaADC","AveWvf","SPEAveWvf"...)
        # "KEY":"AveWvf", # Select key that correcponds to imported wvf runs (e.g. "AnaADC","AveWvf","SPEAveWvf"...)
        "NOISE_AMP": 1,
        # "NORM_DET_RESPONSE": True,
        "FIX_EXP":True,
        "LOGY":True,
        "NORM":False,
        "FOCUS":False,
        "SHOW": True,
        "SHOW_F_SIGNAL":True,
        "SHOW_F_GSIGNAL":True,
        "SHOW_F_DET_RESPONSE":True,
        "SHOW_F_GAUSS":True,
        "SHOW_F_WIENER":True,
        "SHOW_F_DEC":True,
        # "TRIMM": 0,
        "AUTO_TRIMM":False,
        # "WIENER_BUFFER": 800,
        "PRO_RODRIGO": False,
        "THRLD": 1e-4,
        "CONVERT_ADC": True
        }

    dec_run = dict()
    for run in (my_runs["NRun"]):
        dec_run[run] = dict()
        # print(run)
        for ch in (my_runs["NChannel"]):
            # print(ch)
            # print(dec_runs[i])
            dec_run[run][ch] = dict()
            single_response = single_runs[ref_runs[i]][ch]["SPEAvWvf"][0]
            det_response =    light_runs[dec_runs[i]][ch]["AveWvf"][0]
            dec_run[run][ch]["AveWvf"] = [np.max(single_response)*det_response/np.max(det_response)]

    rollcount = 0
    while np.argmax(single_response) < np.argmax(det_response):
        single_response = np.roll(single_response,1)    
        rollcount = rollcount + 1

    # plt.plot(4e-9*np.arange(len(single_response)),single_response/np.max(single_response),c="green",label="Raw SPE signal")
    # plt.plot(4e-9*np.arange(len(single_response)),single_response,c="green",label="Raw SPE signal")
    # plt.plot(4e-9*np.arange(len(det_response)),det_response/np.max(det_response),c="red",label="Raw Laser signal")
    # plt.plot(4e-9*np.arange(len(det_response)),det_response,c="red",label="Raw Laser signal")
    # det_response = np.max(single_response)*det_response/np.max(det_response)
    # plt.plot(4e-9*np.arange(len(det_response)),det_response,label="Norm Laser signal")

    # plt.axhline(0,alpha=0.5,c="black",ls="--")
    # plt.xlabel("Time in [s]");plt.ylabel("Amplitude in ADC counts")
    # plt.legend()
    # plt.show()
    
    deconvolve(my_runs,dec_run,my_runs,keys,OPT)
    save_proccesed_variables(my_runs,"Deconvolution_","../data/dec/")

