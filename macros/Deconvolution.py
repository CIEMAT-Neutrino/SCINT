import sys
sys.path.insert(0, '../')

import numpy as np
import matplotlib.pyplot as plt
from lib.io_functions import load_npy,load_average_npy,load_analysis_npy,load_fit_npy
from lib.dec_functions import deconvolve

run = 26
dec_run = 10
single_run = 2
ch = 6

# my_runs = load_npy([run],[ch])
my_runs = load_average_npy([run],[ch]) # Activate in case deconvolution of average wvf wants to be performed
dec_runs = load_average_npy([dec_run],[ch])
single_runs = load_average_npy([single_run],[ch])

OPT = {
    # "AVE":"ADC",
    "AVE":"AvWvf", # Activate in case deconvolution of average wvf wants to be performed
    # "NORM_DET_RESPONSE": True,
    "FIX_EXP":True,
    "LOGY":False,
    "NORM":False,
    "FOCUS":False,
    "SHOW": True,
    "SHOW_F_SIGNAL":True,
    "SHOW_F_DET_RESPONSE":True,
    "SHOW_F_GAUSS":True,
    "SHOW_F_WIENER":True,
    "SHOW_F_DEC":True,
    "TRIMM": 0,
    "AUTO_TRIMM":False,
    "REVERSE":False,
    # "SMOOTH": 0
    }

# print(dec_runs[dec_run][ch].keys())
single_response = single_runs[single_run][ch]["Single_AvWvf"]
det_response = dec_runs[dec_run][ch]["AvWvf_threshold"]
# det_response = dec_runs[dec_run][ch]["AvWvf"]

# plt.plot(4e-9*np.arange(len(single_response)),single_response/np.max(single_response),c="green",label="Raw SPE signal")
# plt.plot(4e-9*np.arange(len(single_response)),single_response,c="green",label="Raw SPE signal")
# plt.plot(4e-9*np.arange(len(det_response)),det_response/np.max(det_response),c="red",label="Raw Laser signal")
# plt.plot(4e-9*np.arange(len(det_response)),det_response,c="red",label="Raw Laser signal")
# plt.axhline(0,alpha=0.5,c="black",ls="--")
# plt.xlabel("Time in [s]");plt.ylabel("Amplitude in ADC counts")
# plt.legend()
# plt.show()

# det_response = det_response
det_response = np.max(single_response)*det_response/np.max(det_response)

deconvolve(my_runs,det_response,OPT)