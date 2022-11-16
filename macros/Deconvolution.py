import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from itertools import product

from lib.io_functions import load_npy,save_proccesed_variables
from lib.dec_functions import deconvolve

raw_run = [25,26,27]
dec_run = [9,10,11]
ref_run = [1,2,3]
ana_chs = [0,1,6]

for i in range(len(raw_run)):
    my_runs     = load_npy([raw_run[i]],ana_chs,"Average_",      "../data/ave/") # Activate in case deconvolution of average wvf wants to be performed
    light_runs  = load_npy([dec_run[i]],ana_chs,"Average_",      "../data/ave/")
    single_runs = load_npy([ref_run[i]],ana_chs,"Average_",      "../data/ave/")
    out_runs    = load_npy([raw_run[i]],ana_chs,"Deconvolution_","../data/dec/")

    OPT = {
        "KEY":"AvWvf", # Select key that correcponds to imported wvf runs (e.g. "Ana_ADC","AvWvf","SPE_AvWvf"...)
        "NOISE_AMP": 0.05,
        # "NORM_DET_RESPONSE": True,
        "FIX_EXP":True,
        "LOGY":True,
        "NORM":True,
        "FOCUS":False,
        "SHOW": True,
        "SHOW_F_SIGNAL":True,
        "SHOW_F_DET_RESPONSE":True,
        "SHOW_F_GAUSS":True,
        "SHOW_F_WIENER":True,
        "SHOW_F_DEC":True,
        # "TRIMM": 0,
        # "AUTO_TRIMM":False,
        "PRO_RODRIGO": False,
        # "REVERSE":False,
        # "SMOOTH": 0
        }

    dec_runs = dict()
    for run in (my_runs["N_runs"]):
        dec_runs[run] = dict()
        for ch in (my_runs["N_channels"]):
            dec_runs[run][ch] = dict()
            single_response = single_runs[ref_run[i]][ch]["SPE_AvWvf"][0]
            det_response =    light_runs[dec_run[i]][ch]["AvWvf"][0]
            dec_runs[run][ch]["ADC"] = [np.max(single_response)*det_response/np.max(det_response)]

    deconvolve(my_runs,my_runs,dec_runs,OPT)
    save_proccesed_variables(my_runs,"Deconvolution_","../data/dec/")

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