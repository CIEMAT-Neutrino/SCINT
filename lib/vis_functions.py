import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
import keyboard

from .io_functions import load_npy,check_key
from itertools import product
from .cut_functions import *

import scipy
from scipy.signal import find_peaks

from .fig_config import (
    add_grid,
    figure_features,
)  # <--- import customized functions
from matplotlib.colors import LogNorm
from matplotlib.cm import viridis

def vis_npy(my_run, keys, OPT = {}, evt_sel = -1):
    """
    This function is a event visualizer. It plots individual events of a run, indicating the pedestal level, pedestal std and the pedestal calc limit.
    We can interact with the plot and pass through the events freely (go back, jump to a specific event...)
    VARIABLES:
        - my_run: run(s) we want to check
        - KEYS: choose between ADC or AnaADC to see raw (as get from ADC) or Analyzed events (starting in 0 counts), respectively. Type: List
        - OPT: several options that can be True or False. Type: List
            a) NORM: True if we want normalized waveforms
            b) LOGY: True if we want logarithmic y-axis
            c) SHOW_AVE: if computed and True, it will show average
            d) SHOW_PARAM: True if we want to check calculated parameters (pedestal, amplitude, charge...)
            e) CHARGE_KEY: if computed and True, it will show the parametre value
            f) PEAK_FINDER: True if we want to check how many peaks are
        - evt_sel: choose the events we want to see. If -1 all events are displayed, if 0 only uncutted events are displayed, if 1 only cutted events are displayed
    """

    charge_key = "ChargeAveRange"
    if check_key(OPT, "CHARGE_KEY"): charge_key = OPT["CHARGE_KEY"]
    norm_raw = 1
    norm_ave = 1
    buffer = 100
    figure_features()

    plt.ion()
    fig = plt.figure()
    ax = fig.subplots()
    next_plot = False

    for run, ch, key in product(my_run["NRun"],my_run["NChannel"],keys):
        idx = 0

        for i in range(len(my_run[run][ch][key])):
            if evt_sel == 0:
                if my_run[run][ch]["MyCuts"][idx] == False: idx = idx + 1; continue # To Skip Cutted events!!
            elif evt_sel == 1:
                if my_run[run][ch]["MyCuts"][idx] == True: idx = idx + 1; continue # To Get only Cutted events!!
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
            
            # fig = plt.figure()
            # ax = plt.figure().subplots()
            
            plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(raw)),raw,label="RAW_WVF", drawstyle = "steps", alpha = 0.95)
            plt.plot(my_run[run][ch]["Sampling"]*np.array([my_run[run][ch]["PedLim"],my_run[run][ch]["PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw,c="red",lw=2., alpha = 0.8)
            
            if OPT["PEAK_FINDER"]:
                thresh = my_run[run][ch]["PedMax"][idx]
                wdth = 4
                prom = 0.01
                dist  = 40
                peak_idx, _ = find_peaks(raw, height = thresh, width = wdth, prominence = prom, distance=dist)
                for i in peak_idx:
                    plt.scatter(my_run[run][ch]["Sampling"]*i,raw[i],c="tab:red", alpha = 0.9)

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
            cut_opt = 1
            try:
                if my_run[run][ch]["MyCuts"][idx] == False:
                    if cut_opt == 1:
                        figure_features(tex = False)
                        plt.text(0.5,0.5, s = 'CUT', fontsize = 100, horizontalalignment='center',verticalalignment='center',
                                transform = ax.transAxes, color = 'red', fontweight = "bold", alpha = 0.5)
                        figure_features()
                    elif cut_opt != 1: pass
            except: pass
            # plt.title("Run_{} Ch_{} - Event Number {}".format(run,ch,idx),size = 14)
            plt.axhline((ped)/norm_raw,c="k",alpha=.5)
            plt.axhline((ped+std)/norm_raw,c="k",alpha=.5,ls="--"); plt.axhline((ped-std)/norm_raw,c="k",alpha=.5,ls="--")
            plt.legend()

            if OPT["SHOW_PARAM"] == True:
                print("\nEvent Number {} from RUN_{} CH_{} ({})".format(idx,run,ch,my_run[run][ch]["Label"]))
                print("- Sampling: {:.0E}".format(my_run[run][ch]["Sampling"]))
                print("- Pedestal mean: {:.2E}".format(my_run[run][ch]["PedMean"][idx]))
                print("- Pedestal std: {:.4f}".format(my_run[run][ch]["PedSTD"][idx]))
                print("- Pedestal min: {:.4f}\t Pedestal max {:.4f}".format(my_run[run][ch]["PedMin"][idx],my_run[run][ch]["PedMax"][idx]))
                print("- Pedestal time limit: {:.4E}".format(my_run[run][ch]["Sampling"]*my_run[run][ch]["PedLim"]))
                print("- Max Peak Amplitude: {:.4f}".format(my_run[run][ch]["PeakAmp"][idx]))
                print("- Max Peak Time: {:.2E}".format(my_run[run][ch]["PeakTime"][idx]*my_run[run][ch]["Sampling"]))
                try:
                    print("- Charge: {:.2E}".format(my_run[run][ch][OPT["CHARGE_KEY"]][idx]))
                except:
                    if check_key(OPT,"CHARGE_KEY"): print("- Charge: has not been computed for key %s!"%OPT["CHARGE_KEY"])
                    else: print("- Charge: default charge key has not been computed")
                # if check_key(OPT, "PEAK_FINDER") == True:
                try:
                    print("- Peak_idx:",peak_idx*my_run[run][ch]["Sampling"])
                except:
                    if not check_key(OPT,"PEAK_FINDER"): print("")

            tecla = input("\nPress q to quit, r to go back, n to choose event or any key to continue: ")
            if tecla == "q":
                break
            elif tecla == "r":
                idx = idx-1
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                idx = ev_num
                if idx > len(my_run[run][ch][key]): idx = len(my_run[run][ch][key])-1; print('\033[1m' + "\nBe careful! There are ", idx, "in total"); print('\033[0m')
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

def vis_persistence(my_run, OPT = {}):
    """
    This function plot the PERSISTENCE histogram of the given runs&ch.
    It perfoms a cut in 20<"PeakTime"(bins)<50 so that all the events not satisfying the condition are removed. 
    Binning is fixed (x=5000, y=1000) [study upgrade].
    X_data (time) and Y_data (waveforms) are deleted after the plot to save space.
    WARNING! flattening long arrays leads to MEMORY problems :/
    """

    plt.ion()
    for run, ch in product(my_run["NRun"],my_run["NChannel"]):

        generate_cut_array(my_run)
        cut_min_max(my_run, ["PeakTime"], {"PeakTime":[my_run[run][ch]["PedLim"]-20,my_run[run][ch]["PedLim"]+50]})

        data_flatten = my_run[run][ch]["AnaADC"][np.where(my_run[run][ch]["MyCuts"] == True)].flatten() #####
        time = my_run[run][ch]["Sampling"]*np.arange(len(my_run[run][ch]["AnaADC"][0]))
        time_flatten = np.array([time] * int(len(data_flatten)/len(time))).flatten()

        plt.hist2d(time_flatten,data_flatten,density=True,bins=[5000,1000], cmap = viridis, norm=LogNorm())

        plt.colorbar()
        plt.grid(True, alpha = 0.7) # , zorder = 0 for grid behind hist
        plt.title("Run_{} Ch_{} - Persistence".format(run,ch),size = 14)
        plt.xticks(size = 11); plt.yticks(size = 11)
        plt.xlabel("Time (s)", size = 11); plt.ylabel("Counts", size = 11)
        del data_flatten, time, time_flatten
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    plt.ioff()
    plt.clf()