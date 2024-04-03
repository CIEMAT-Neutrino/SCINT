import sys
sys.path.insert(0, '../../')
from lib.io_functions import load_npy, save_proccesed_variables
from lib.fit_functions import scfunc, gauss
from lib.sim_functions import rand_scint_times
from lib.wvf_functions import find_baseline_cuts, find_amp_decrease
from lib.dec_functions import deconvolve

import uproot
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from scipy.optimize import curve_fit

plt.rcParams.update({'font.size': 15})

# Generate dict framework structure
info = { "PATH": [f"{root}/_data/"],
        "MONTH": ["SC_Test"]}

my_run = dict()
my_run["NRun"] = []
my_run["NChannel"] = []
template_list = ["{root}/data/SC_Test/raw/wvf_config_1.npy","{root}/data/SC_Test/raw/wvf_config_2.npy","{root}/data/SC_Test/raw/wvf_config_3.npy"]

# Each template is a run
for i in range(len(template_list)):
    my_run[i+1] = dict()
    my_run["NRun"].append(i+1)
    # For each run ch variable can be used to test different features (in this case template length)
    for j in np.linspace(500,1000,6).astype(str):
        # Load list of template files
        SER = []
        for template in template_list:
            SER.append(np.load(template))
        
        my_run["NChannel"].append(int(j))
        my_run[i+1][j] = dict()
        my_run[i+1][j]["Sampling"] = 16e-9
        my_run[i+1][j]["TimeWindow"] = int(j)  # Length of wvf array [ticks]
        my_run[i+1][j]["PreTrigger"] = 100 # Additional before signal [ticks]
        # Generate empty array to import data
        i_idx,f_idx = find_amp_decrease(SER[i], 1e-4)
        i_base_idx,f_base_idx = find_baseline_cuts(SER[i])
        my_run[i+1][j]["SPEChargeADC"] = my_run[i+1][j]["Sampling"]*np.sum(10*SER[i][i_idx:f_base_idx]/np.max(SER[i]))
        SER[i] = np.asarray(SER[i][i_idx:])
        
        if np.size(SER[i]) > my_run[i+1][j]["TimeWindow"]:
            SER[i] = SER[i][:np.size(SER[i])-my_run[i+1][j]["TimeWindow"]]
        elif np.size(SER[i]) < my_run[i+1][j]["TimeWindow"]:
            SER[i] = np.concatenate((SER[i],np.zeros(my_run[i+1][j]["TimeWindow"]-np.size(SER[i]))))

        SER[i] = np.resize(SER[i],my_run[i+1][j]["TimeWindow"])
        my_run[i+1][j]["SPE"] = [10*np.array(SER[i])/np.max(np.array(SER[i]))]

        # cutoff = 2.56e6 # Cutoff frequency in [Hz]
        cutoff = 2e6 # Cutoff frequency in [Hz]
        my_run[i+1][j]["GaussCutOff"] = my_run[i+1][j]["TimeWindow"]*cutoff*my_run[i+1][j]["Sampling"]
        plt.plot(np.arange(0,j,1),my_run[i+1][j]["SPE"][0])
        plt.show()

save_proccesed_variables(my_run,preset="ALL",info=info,force=True)