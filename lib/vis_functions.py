import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
import keyboard

from .io_functions import load_npy,check_key
from itertools import product

import scipy
from scipy.signal import find_peaks

from .fig_config import (
    add_grid,
    figure_features,
)  # <--- import customized functions

def vis_npy(my_run, keys, OPT):
    """
    This function is a event visualizer. It plots individual events of a run, indicating the pedestal level, pedestal std and the pedestal calc limit.
    We can interact with the plot and pass through the events freely (go back, jump to a specific event...)
    VARIABLES:
        - my_run: run(s) we want to check
        - KEYS: choose between ADC or AnaADC to see raw (as get from ADC) or Analyzed events (starting in 0 counts), respectively. Type: List
        - OPT: several options that can be True or False. Type: List
            a) NORM: True if we want normalized waveforms
            b) LOGY: True if we want logarithmic y-axis
            c) SHOW_PARAM: True if we want to check calculated parameters (pedestal, amplitude, charge...)
    """

    charge_key = "ChargeAveRange"
    if check_key(OPT, "CHARGE_KEY"): charge_key = OPT["CHARGE_KEY"]
    norm_raw = 1
    norm_ave = 1
    buffer = 100
    figure_features()

    plt.ion()
    next_plot = False

    for run, ch, key in product(my_run["NRun"],my_run["NChannel"],keys):
        idx = 0

        for i in range(len(my_run[run][ch][key])):
            plt.xlabel("Time [s]")
            plt.ylabel("ADC Counts")
            plt.grid(True, alpha = 0.7)
            # add_grid(ax, locations = (5, 10, 5, 10))  # <--- Add this line to every figure

            
            if (key == "ADC"):
                min = np.argmin(my_run[run][ch][key][idx])
                raw = my_run[run][ch][key][idx]
                ped = np.mean(my_run[run][ch][key][idx][:min-buffer])
                std = np.std(my_run[run][ch][key][idx][:min-buffer])
                COL = "tab:blue"
            
            elif(key == "AnaADC"):
                min = np.argmax(my_run[run][ch][key][idx])
                raw = my_run[run][ch][key][idx]
                ped = 0    
                std = my_run[run][ch]["PedSTD"][idx]

            if OPT["NORM"] == True and OPT["NORM"] == True:
                norm_raw = np.max(raw)
                raw = raw/np.max(raw)
            
            plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(raw)),raw,label="RAW_WVF", drawstyle = "steps", alpha = 0.9)
            plt.plot(my_run[run][ch]["Sampling"]*np.array([my_run[run][ch]["PedLim"],my_run[run][ch]["PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw,c="red",lw=2., alpha = 0.8)

            # thresh = int(len(my_run[run][ch][key])/1000)
            thresh = int(20)
            wdth = 4
            prom = 0.01
            dist  = 40
            # peak_idx, _ = find_peaks(np.log10(y), height = np.log10(thresh), width = wdth, prominence = prom)
            peak_idx, _ = find_peaks(raw, height = thresh, width = wdth, prominence = prom, distance=dist)
            for i in peak_idx:
                # print(raw[i])
                # print(my_run[run][ch]["Sampling"]*i)
                plt.scatter(my_run[run][ch]["Sampling"]*i,raw[i],c="tab:red")

            if check_key(OPT, "SHOW_AVE") == True:   
                try:
                    ave_key = OPT["SHOW_AVE"]
                    ave = my_run[run][ch][ave_key][0]
                    if OPT["NORM"] == True and OPT["NORM"] == True:
                        ave = ave/np.max(ave)
                    plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(ave)),ave,alpha=.5,label="AVE_WVF_%s"%ave_key)             
                except:
                    print("Run has not been averaged!")
                        
            if OPT["LOGY"] == True:
                plt.semilogy()

            plt.title("Run_{} Ch_{} - Event Number {}".format(run,ch,idx),size = 14)
            plt.axhline((ped)/norm_raw,c="k",alpha=.5)
            plt.axhline((ped+std)/norm_raw,c="k",alpha=.5,ls="--"); plt.axhline((ped-std)/norm_raw,c="k",alpha=.5,ls="--")
            plt.legend()

            if OPT["SHOW_PARAM"] == True:
                print("Event Number {} from RUN_{} CH_{} ({})".format(idx,run,ch,my_run[run][ch]["Label"]))
                print("- Sampling: {:.0E}".format(my_run[run][ch]["Sampling"]))
                print("- Pedestal mean: {:.2E}".format(my_run[run][ch]["PedMean"][idx]))
                print("- Pedestal std: {:.4f}".format(my_run[run][ch]["PedSTD"][idx]))
                print("- Pedestal min: {:.4f}\t Pedestal max {:.4f}".format(my_run[run][ch]["PedMin"][idx],my_run[run][ch]["PedMax"][idx]))
                print("- Pedestal time limit: {:.4E}".format(my_run[run][ch]["Sampling"]*my_run[run][ch]["PedLim"]))
                print("- Max Peak Amplitude: {:.4f}".format(my_run[run][ch]["PeakAmp"][idx]))
                print("- Max Peak Time: {:.2E}".format(my_run[run][ch]["PeakTime"][idx]*my_run[run][ch]["Sampling"]))
                print("Peak_idx", peak_idx)
                try:
                    print("- Charge: {:.2E}\n".format(my_run[run][ch][OPT["CHARGE_KEY"]][idx]))
                except:
                    if check_key(OPT,"CHARGE_KEY"): print("- Charge: has not been computed for key %s!"%OPT["CHARGE_KEY"])
                    else: print("- Charge: defualt charge key has not been computed")

            tecla = input("\nPress q to quit, r to go back, n to choose event or any key to continue: ")
            if tecla == "q":
                break
            elif tecla == "r":
                idx = idx-1
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                idx = ev_num
                if idx > len(my_run[run][ch][key]): idx = len(my_run[run][ch][key])-1
            else:
                idx = idx + 1
                # while not plt.waitforbuttonpress(-1): pass           
            if idx == len(my_run[run][ch][key]): break
            plt.clf()
        plt.clf()
    plt.ioff()
    plt.clf()

def vis_var_hist(my_run, keys, percentile = [0.1, 99.9], OPT = {}):
    """
    This function takes the specified variables and makes histograms. The binning is fix to 600, so maybe it is not the appropriate.
    Outliers are taken into account with the percentile. It discards values below and above the indicated percetiles.
    It returns values of counts, bins and bars from the histogram to be used in other function.
    VARIABLES:
        - my_run: run(s) we want to check
        - keys: variables we want to plot as histograms. Type: List
            a) PeakAmp: histogram of max amplitudes of all events. The binning is 1 ADC. There are not outliers.
            b) PeakTime: histogram of times of the max amplitude in events. The binning is the double of the sampling. There are not outliers.
            c) Other variable: any other variable. Here we reject outliers.
        - percentile: percentile used for outliers removal
    WARNING! Maybe the binning stuff should be studied in more detail.
    """
    # keys is the variable that we want to plot
    w=1e-4 # w is related to the bin width in some way
    figure_features()

    plt.ion()
    all_counts = []
    all_bins = []
    all_bars = []
    for run, ch, key in product(my_run["NRun"],my_run["NChannel"],keys):
        # w = abs(np.max(my_run[run][ch][key])-np.min(my_run[run][ch][key]))*w
        data = []
        if key == "PeakAmp":
            data = my_run[run][ch][key]
            max_amp = np.max(data)
            binning = int(max_amp)+1
        elif key == "PeakTime":
            data = my_run[run][ch]["Sampling"]*my_run[run][ch][key]
            binning = int(my_run[run][ch]["NBinsWvf"]/2)
        else:
            data = my_run[run][ch][key]
            ypbot = np.percentile(data, percentile[0]); yptop = np.percentile(data, percentile[1])
            ypad = 0.2*(yptop - ypbot)
            ymin = ypbot - ypad; ymax = yptop + ypad
            data = [i for i in data if ymin<i<ymax]
            w = abs(np.max(data)-np.min(data))*w
            binning = 600 # FIXED VALUE UNTIL BETTER SOLUTION
            # binning = np.arange(min(data), max(data) + w, w)
            # binning = int((np.max(data)-np.min(data)) * len(data)**(1/3) / (3.49*np.std(data)))*5 # Visto por internete
            # print(w)
            # print(len(binning))
            # if len(binning) < 100: binning = 100
            # if len(binning) > 2000: binning = 1000
            # AALTERNATIVE WAY OF FILTERING OUTLIERS
            # data=sorted(data)
            # out_threshold= 2.0*np.std(data+[-a for a in data]) # Repeat distribution in negative axis to compute std
            # data=[i for i in data if -out_threshold<i<out_threshold]
            # binning = np.arange(min(data), max(data) + w, w)


        counts, bins, bars = plt.hist(data,binning) # , zorder = 2 f
        all_counts.append(counts)
        all_bins.append(bins)
        all_bars.append(bars)
        plt.grid(True, alpha = 0.7) # , zorder = 0 for grid behind hist
        plt.title("Run_{} Ch_{} - {} histogram".format(run,ch,key),size = 14)
        plt.xticks(size = 11); plt.yticks(size = 11)
        plt.xlabel(key+" (Units)", size = 11); plt.ylabel("Counts", size = 11)
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    plt.ioff()
    return all_counts, all_bins, all_bars