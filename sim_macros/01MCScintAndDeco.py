import sys
sys.path.insert(0, '../')
from lib.io_functions import load_npy, save_proccesed_variables
from lib.fit_functions import fit_wvfs,scfunc, gauss
from lib.sim_functions import rand_scint_times
from lib.wvf_functions import find_baseline_cuts, find_amp_decrease
from lib.dec_functions import deconvolve

import uproot
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from scipy.optimize import curve_fit

plt.rcParams.update({'font.size': 15})

info = {"MONTH": ["SC_Test"]}

my_run = load_npy([1,2,3],[500,600,700,800,900,1000], preset="ALL", info=info)
MC_num = 1000 # Number of mc wvf to be generated
for run, ch in product(my_run["NRun"],my_run["NChannel"]):
    buffer = 4*my_run[run][ch]["TimeWindow"]  # Buffer expanding array to accomodate scint wvfs [ticks]
    my_run[run][ch]["McADC"] = []
    my_run[run][ch]["Mct0"] = []
    for jj in range(MC_num):
        times = rand_scint_times(100,fast=6e-9,slow=1.4e-6,ratio=0.7)                        # Main mc function generates photon arrival times
        wvf = np.zeros(buffer)
        for t in times:
            this_peak = int((t-(t%my_run[run][ch]["Sampling"]))/my_run[run][ch]["Sampling"]) # Calculate the modulus of the arrival time according to sampling.
            this_wvf = np.zeros(my_run[run][ch]["PreTrigger"]+this_peak)
            this_wvf = np.append(this_wvf,my_run[run][ch]["SPE"][0])
            this_wvf = np.append(this_wvf,np.zeros(len(wvf)-len(this_wvf))) # If this line gives errors, make buffer bigger
            wvf = wvf+this_wvf

        my_run[run][ch]["McADC"].append(wvf[:my_run[run][ch]["TimeWindow"]])
        my_run[run][ch]["Mct0"].append(times[0])
    
    my_run[run][ch]["Mct0"] = np.asarray(my_run[run][ch]["Mct0"])
    my_run[run][ch]["McNoiseADC"] = np.asarray(my_run[run][ch]["McADC"])+np.random.normal(0,np.max(my_run[run][ch]["SPE"])*0.5,size=[len(my_run[run][ch]["McADC"]),len(my_run[run][ch]["McADC"][0])])

OPT = {
"NOISE_AMP": 0.5, # Noise amp as a factor of SPE max.
"FIX_EXP":True,
"WIENER_BUFFER": 50,
"CONVERT_ADC": False
}

OPT["FILTER"] = "WIENER"
KEY = ["McADC","SPE","DecADC"]
deconvolve(my_run,my_run,my_run,KEY,OPT)

KEY = ["McNoiseADC","SPE","DecNoiseADC"]
deconvolve(my_run,my_run,my_run,KEY,OPT)

OPT["FILTER"] = "GAUSS"
KEY = ["McADC","SPE","DecADC"]
deconvolve(my_run,my_run,my_run,KEY,OPT)

KEY = ["McNoiseADC","SPE","DecNoiseADC"]
deconvolve(my_run,my_run,my_run,KEY,OPT)

raw_key = ["McNoiseADC","GaussDecNoiseADC","WienerDecNoiseADC"]
wvf_key = ["Raw","Gauss","Wiener"]

for run, ch in product(my_run["NRun"],my_run["NChannel"]):
    for j in range(len(raw_key)):
        my_run[run][ch][wvf_key[j]+"Charge"] = []
        my_run[run][ch][wvf_key[j]+"Amp"] = []
        my_run[run][ch][wvf_key[j]+"Time"] = [] 
        my_run[run][ch][wvf_key[j]+"NoiseSTD"] = [] 
        for i in range(len(my_run[run][ch][raw_key[j]])):
            i_base_idx,f_base_idx = find_baseline_cuts(my_run[run][ch][raw_key[j]][i])
            amp = np.max(my_run[run][ch][raw_key[j]][i])
            time = my_run[run][ch]["Sampling"]*(np.argmax(my_run[run][ch][raw_key[j]][i])-my_run[run][ch]["PreTrigger"] + 1) - my_run[run][ch]["Mct0"][i]
            noiseSTD = np.std(my_run[run][ch][raw_key[j]][i][:i_base_idx])
            
            if raw_key[j] == "McNoiseADC":
                charge = np.sum(my_run[run][ch][raw_key[j]][i][i_base_idx:f_base_idx])
                my_run[run][ch][wvf_key[j]+"Charge"].append(my_run[run][ch]["Sampling"]*charge/my_run[run][ch]["SPEChargeADC"]) 
            
            else:
                charge = np.sum(my_run[run][ch][raw_key[j]][i][my_run[run][ch]["PreTrigger"]-20:])
                my_run[run][ch][wvf_key[j]+"Charge"].append(charge)
            my_run[run][ch][wvf_key[j]+"Amp"].append(amp)
            my_run[run][ch][wvf_key[j]+"Time"].append(time*1e9)
            my_run[run][ch][wvf_key[j]+"NoiseSTD"].append(noiseSTD)
        my_run[run][ch][wvf_key[j]+"Charge"]   = np.asarray(my_run[run][ch][wvf_key[j]+"Charge"])
        my_run[run][ch][wvf_key[j]+"Amp"]      = np.asarray(my_run[run][ch][wvf_key[j]+"Amp"])
        my_run[run][ch][wvf_key[j]+"Time"]     = np.asarray(my_run[run][ch][wvf_key[j]+"Time"])
        my_run[run][ch][wvf_key[j]+"NoiseSTD"] = np.asarray(my_run[run][ch][wvf_key[j]+"NoiseSTD"])

save_proccesed_variables(my_run,preset="ALL",info=info,force=True)