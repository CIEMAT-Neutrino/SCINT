import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt

from lib.io_functions import load_npy,save_proccesed_variables
from lib.dec_functions import deconvolve

run = 2
dec_run = 10
single_run = 2
ch = 6

# my_runs = load_npy([run],[ch],"Analysis_","../data/ana/") # Activate in case deconvolution of average wvf wants to be performed
my_runs = load_npy([run],[ch],"Average_","../data/ave/") # Activate in case deconvolution of average wvf wants to be performed

dec_runs = load_npy([dec_run],[ch],"Average_","../data/ave/")
single_runs = load_npy([single_run],[ch],"Average_","../data/ave/")

out_runs = load_npy([run],[ch],"Deconvolution_","../data/dec/")

OPT = {
    "KEY":"SPE_AvWvf", # Select key that correcponds to imported wvf runs (e.g. "Ana_ADC","AvWvf","SPE_AvWvf"...)
    # "NORM_DET_RESPONSE": True,
    "FIX_EXP":True,
    "LOGY":False,
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

single_response = single_runs[single_run][ch]["SPE_AvWvf"][0]
det_response = dec_runs[dec_run][ch]["AvWvf"][0]

det_response = np.max(single_response)*det_response/np.max(det_response)

deconvolve(my_runs,out_runs,det_response,OPT)

save_proccesed_variables(out_runs,"Deconvolution_","../data/dec/")

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