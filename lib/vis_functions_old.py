import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.cm import viridis
import numpy as np
import keyboard
import math
from itertools import product
from scipy.ndimage.interpolation import shift

from .io_functions import load_npy,check_key, print_keys
from .ana_functions import generate_cut_array, get_units
from .fit_functions import gaussian, scint_fit, fit_wvfs, gaussian_fit

import scipy
from scipy.signal import find_peaks

from .fig_config import (
    add_grid,
    figure_features,
)

def vis_npy(my_run, keys, evt_sel = -1, same_plot = False, OPT = {}, debug = False):
    """
    This function is a event visualizer. It plots individual events of a run, indicating the pedestal level, pedestal std and the pedestal calc limit.
    We can interact with the plot and pass through the events freely (go back, jump to a specific event...)
    VARIABLES:
        - my_run: run(s) we want to check
        - KEYS: choose between ADC or AnaADC to see raw (as get from ADC) or Analyzed events (starting in 0 counts), respectively. Type: List
        - OPT: several options that can be True or False. Type: List
            a) MICRO_SEC: if True we multiply Sampling by 1e6
            b) NORM: True if we want normalized waveforms
            c) LOGY: True if we want logarithmic y-axis
            d) SHOW_AVE: if computed and True, it will show average
            e) SHOW_PARAM: True if we want to check calculated parameters (pedestal, amplitude, charge...)
            f) CHARGE_KEY: if computed and True, it will show the parametre value
            g) PEAK_FINDER: True if we want to check how many peaks are
        - evt_sel: choose the events we want to see. If -1 all events are displayed, if 0 only uncutted events are displayed, if 1 only cutted events are displayed
        - same_plot: True if we want to plot different channels in the SAME plot
    """

    figure_features()
    charge_key = "ChargeAveRange"
    if check_key(OPT, "CHARGE_KEY"): charge_key = OPT["CHARGE_KEY"]
    norm_ave = 1
    buffer = 100

    ch_list = my_run["NChannel"]
    nch = len(my_run["NChannel"])
    axs = []

    for run, key in product(my_run["NRun"],keys):
        plt.ion()
        if same_plot == False:
            if nch < 4:
                fig, ax = plt.subplots(nch ,1, figsize = (10,8))
                if nch == 1: axs.append(ax)
                else: axs = ax
            else:
                fig, ax = plt.subplots(2, math.ceil(nch/2), figsize = (10,8))
                axs = ax.T.flatten()
        else:
            fig, ax = plt.subplots(1 ,1, figsize = (8,6))
            axs = ax
        idx = 0
        for i in range(len(my_run[run][ch_list[0]][key])):
            try:
                skip = 0
                for ch in ch_list:
                    if evt_sel == 0 and my_run[run][ch]["MyCuts"][idx] == False: skip = 1; break # To Skip Cutted events!!
                    if evt_sel == 1 and my_run[run][ch]["MyCuts"][idx] == True:  skip = 1; break # To Get only Cutted events!!
                if skip == 1: idx = idx +1; continue
            except: pass

            fig.supxlabel(r'Time [s]')
            fig.supylabel("ADC Counts")
            min = []
            raw = []
            norm_raw = [1]*nch # Generates a list with the norm correction for std bar
            for j in range(nch):
                if (key == "RawADC"):
                    min.append(np.argmin(my_run[run][ch_list[j]][key][idx]))
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = np.mean(my_run[run][ch_list[j]][key][idx][:min[j]-buffer])
                    std = np.std(my_run[run][ch_list[j]][key][idx][:min[j]-buffer])
                    label = "Raw"
                    if debug: 
                        print("Using '%s' label"%label)
                elif(key == "ADC"):
                    min.append(np.argmax(my_run[run][ch_list[j]][key][idx]))
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = 0
                    std = my_run[run][ch_list[j]]["PedSTD"][idx]
                    label = ""
                    if debug: 
                        print((my_run[run][ch_list[j]][key][idx]).dtype)
                        print("Using '%s' label"%label)

                elif("ADC" in str(key)):
                    min.append(np.argmax(my_run[run][ch_list[j]][key][idx]))
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = 0
                    std = np.std(my_run[run][ch_list[j]][key][idx][:min[j]-buffer])
                    label = key.replace("ADC","")
                    if debug: 
                        print((my_run[run][ch_list[j]][key][idx]).dtype)
                        print("Using '%s' label"%label)

                elif("Ave" in str(key)):
                    min.append(np.argmax(my_run[run][ch_list[j]][key][idx]))
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = 0
                    std = np.std(my_run[run][ch_list[j]][key][idx][:min[j]-buffer])
                    label = key.replace("Ave","")
                    if debug: print("Using '%s' label"%label)

                if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
                    norm_raw[j] = (np.max(raw[j]))
                    raw[j] = raw[j]/np.max(raw[j])

                sampling = my_run[run][ch_list[j]]["Sampling"] # To reset the sampling to its initial value (could be improved)
                if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"]==True:
                    fig.supxlabel(r'Time [$\mu$s]')
                    my_run[run][ch_list[j]]["Sampling"] = my_run[run][ch_list[j]]["Sampling"]*1e6

                if same_plot == False:
                    if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                        axs[j].semilogy()
                        std = 0 # It is ugly if we see this line in log plots
                    # fig.tight_layout(h_pad=2) # If we want more space betweeb subplots. We avoid small vertical space between plots            
                    axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(raw[j])),raw[j],label="RAW_WVF", drawstyle = "steps", alpha = 0.95, linewidth=1.2)
                    axs[j].grid(True, alpha = 0.7)
                    try:
                        axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.array([my_run[run][ch_list[j]][label+"PedLim"],my_run[run][ch_list[j]][label+"PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw[j],c="red",lw=2., alpha = 0.8)
                        axs[j].axhline((ped)/norm_raw[j],c="k",alpha=.55)
                        axs[j].axhline((ped+std)/norm_raw[j],c="k",alpha=.5,ls="--"); axs[j].axhline((ped-std)/norm_raw[j],c="k",alpha=.5,ls="--")
                    except KeyError:
                        print("Run preprocess please!")
                    axs[j].set_title("Run {} - Ch {} - Event Number {}".format(run,ch_list[j],idx),size = 14)
                    axs[j].xaxis.offsetText.set_fontsize(14) # Smaller fontsize for scientific notation
                    
                    if check_key(OPT, "SHOW_AVE") == True:   
                        try:
                            ave_key = OPT["SHOW_AVE"]
                            ave = my_run[run][ch_list[j]][ave_key][0]
                            if OPT["NORM"] == True and OPT["NORM"] == True:
                                ave = ave/np.max(ave)
                            if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                                ref_max_idx = np.argmax(raw[j])
                                idx_move = np.argmax(ave)
                                ave = shift(ave, ref_max_idx-idx_move, cval = 0)
                            axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(ave)),ave,alpha=.5,label="AVE_WVF_%s"%ave_key, drawstyle = "steps")             
                        except KeyError:
                            print("Run has not been averaged!")

                    if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
                        axs[j].legend()

                    if check_key(OPT, "PEAK_FINDER") == True and OPT["PEAK_FINDER"]:
                        # These parameters must be modified according to the run...
                        if check_key(my_run[run][ch_list[j]], "AveWvfSPE") == False:
                            thresh = my_run[run][ch_list[j]]["PedMax"][idx] + 0.5*my_run[run][ch_list[j]]["PedMax"][idx]
                        else:
                            thresh = np.max(my_run[run][ch_list[j]]["AveWvfSPE"])*3/4
                        wdth = 4
                        prom = 0.01
                        dist  = 30
                        axs[j].axhline(thresh,c="k", alpha=.6, ls = "dotted")
                        peak_idx, _ = find_peaks(raw[j], height = thresh, width = wdth, prominence = prom, distance=dist)
                        for p in peak_idx:
                            axs[j].scatter(my_run[run][ch_list[j]]["Sampling"]*p,raw[j][p],c="tab:red", alpha = 0.9)

                    try:
                        if my_run[run][ch_list[j]]["MyCuts"][idx] == False:
                            figure_features(tex = False)
                            axs[j].text(0.5,0.5, s = 'CUT', fontsize = 100, horizontalalignment='center',verticalalignment='center',
                                        transform = axs[j].transAxes, color = 'red', fontweight = "bold", alpha = 0.5)
                            figure_features()
                    except: pass
                
                else:
                    if check_key(OPT, "LOGY") == True and OPT["LOGY"]:
                        axs.semilogy()
                        std = 0 # It is ugly if we see this line in log plots
                    axs.plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(raw[j])),raw[j], drawstyle = "steps", alpha = 0.95, linewidth=1.2, label = "Ch {} ({})".format(ch_list[j],my_run[run][ch_list[j]]["Label"]))
                    axs.grid(True, alpha = 0.7)
                    try:
                        axs.plot(my_run[run][ch_list[j]]["Sampling"]*np.array([my_run[run][ch_list[j]][label+"PedLim"],my_run[run][ch_list[j]][label+"PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw[j],c="red",lw=2., alpha = 0.8)
                    except KeyError:
                        print("Run preprocess please!")
                    axs.set_title("Run {} - Event Number {}".format(run,idx),size = 14)
                    axs.xaxis.offsetText.set_fontsize(14)
                    
                    if check_key(OPT, "SHOW_AVE") == True:   
                        try:
                            ave_key = OPT["SHOW_AVE"]
                            ave = my_run[run][ch_list[j]][ave_key][0]
                            if OPT["NORM"] == True and OPT["NORM"] == True:
                                ave = ave/np.max(ave)
                            if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                                ref_max_idx, = np.where(ave == np.max(ave))
                                idx, = np.where(ave == np.max(ave))
                                ave = shift(ave, ref_max_idx-idx, cval = 0)
                            axs.plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(ave)),ave,alpha=.5,label="AVE_WVF_%s"%ave_key)             
                        except KeyError: print("Run has not been averaged!")

                    if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
                        axs.legend()

                    if check_key(OPT, "PEAK_FINDER") == True and OPT["PEAK_FINDER"]:
                        # These parameters must be modified according to the run...
                        thresh = my_run[run][ch_list[j]]["PedMax"][idx]
                        wdth = 4
                        prom = 0.01
                        dist = 40
                        axs.axhline(thresh,c="salmon", alpha=.6, ls = "dotted")
                        # peak_idx, _ = find_peaks(raw[j], height = thresh, width = wdth, prominence = prom, distance=dist)
                        peak_idx, _ = find_peaks(raw[j], height = thresh)       
                        for p in peak_idx:
                            axs.scatter(my_run[run][ch_list[j]]["Sampling"]*p,raw[j][p],c="tab:red", alpha = 0.9)

                    try:
                        if my_run[run][ch_list[j]]["MyCuts"][idx] == False:
                            figure_features(tex = False)
                            axs.text(0.5,0.5, s = 'CUT', fontsize = 100, horizontalalignment='center',verticalalignment='center',
                                        transform = axs.transAxes, color = 'red', fontweight = "bold", alpha = 0.5)
                            figure_features()
                    except: pass
                    
                if check_key(OPT, "SHOW_PARAM") == True and OPT["SHOW_PARAM"]:
                    print('\033[1m' + "\nEvent Number {} from RUN_{} CH_{} ({})".format(idx,run,ch_list[j],my_run[run][ch_list[j]]["Label"]) + '\033[0m')
                    print("- Sampling: {:.0E}".format(sampling))
                    print("- Pedestal mean: {:.2E}".format(my_run[run][ch_list[j]][label+"PedMean"][idx]))
                    print("- Pedestal std: {:.4f}".format(my_run[run][ch_list[j]][label+"PedSTD"][idx]))
                    print("- Pedestal min: {:.4f}\t Pedestal max {:.4f}".format(my_run[run][ch_list[j]][label+"PedMin"][idx],my_run[run][ch_list[j]][label+"PedMax"][idx]))
                    print("- Pedestal time limit: {:.4E}".format(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"PedLim"]))
                    print("- Max Peak Amplitude: {:.4f}".format(my_run[run][ch_list[j]][label+"PeakAmp"][idx]))
                    print("- Max Peak Time: {:.2E}".format(my_run[run][ch_list[j]][label+"PeakTime"][idx]*my_run[run][ch_list[j]]["Sampling"]))
                    try:
                        print("- Charge: {:.2E}".format(my_run[run][ch_list[j]][OPT["CHARGE_KEY"]][idx]))
                    except:
                        if check_key(OPT,"CHARGE_KEY"): print("- Charge: has not been computed for key %s!"%OPT["CHARGE_KEY"])
                        else: print("- Charge: default charge key has not been computed")
                    try:
                        print("- Peak_idx:",peak_idx*my_run[run][ch_list[j]]["Sampling"])
                    except:
                        if not check_key(OPT,"PEAK_FINDER"): print("")
                my_run[run][ch_list[j]]["Sampling"] = sampling    

            tecla = input("\nPress q to quit, p to save plot, r to go back, n to choose event or any key to continue: ")

            if tecla == "q":
                break
            elif tecla == "r":
                idx = idx-1
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                idx = ev_num
                if idx > len(my_run[run][ch_list[j]][key]): idx = len(my_run[run][ch_list[j]][key])-1; print('\033[1m' + "\nBe careful! There are ", idx, "in total"); print('\033[0m')
            elif tecla == "p":
                fig.savefig('run{}_evt{}.png'.format(run,idx), dpi = 500)
                idx = idx+1
            else:
                idx = idx + 1
            if idx == len(my_run[run][ch_list[j]][key]): break
            try: [axs[j].clear() for j in range (nch)]
            except: axs.clear()
        try: [axs[j].clear() for j in range (nch)]
        except: axs.clear()
        plt.close()

def vis_compare_wvf(my_run, keys, compare="RUNS", OPT = {}):
    """
    This function is a waveform visualizer. It plots the selected waveform with the key and allow comparisson between runs/channels.
    VARIABLES:
        - my_run: run(s) we want to check
        - KEYS: waveform to plot (AveWvf, AveWvdSPE, ...). Type: List
        - OPT: several options that can be True or False.  Type: List
            a) MICRO_SEC: if True we multiply Sampling by 1e6
            b) NORM: True if we want normalized waveforms
            c) LOGY: True if we want logarithmic y-axis
        - compare: 
            a) "RUNS" to get a plot for each channel and the selected runs. Type: String
            b) "CHANNELS" to get a plot for each run and the selected channels. Type: String
    """

    figure_features()

    r_list = my_run["NRun"]
    ch_list = my_run["NChannel"]
    nch = len(my_run["NChannel"])
    axs = []
    
    if compare == "CHANNELS":
        a_list = r_list 
        b_list = ch_list 
    if compare == "RUNS":
        a_list = ch_list 
        b_list = r_list 

    for a in a_list:
        if compare == "CHANNELS": run = a
        if compare == "RUNS":      ch = a

        plt.ion()
        fig, ax = plt.subplots(1 ,1, figsize = (8,6))
        axs = ax

        fig.supxlabel(r'Time [s]')
        fig.supylabel("ADC Counts")
        # fig.supylabel("Normalized Amplitude")
        norm_raw = [1]*nch # Generates a list with the norm correction for std bar
        counter = 0
        ref_max_idx = -1
        for b in b_list:
            if compare == "CHANNELS": ch = b; label = "Channel {} ({}) - {}".format(ch,my_run[run][ch]["Label"],keys[counter]); title = "Average Waveform - Run {}".format(run)
            if compare == "RUNS":    run = b; label = "Run {} - {}".format(run,keys[counter]); title = "Average Waveform - Ch {} ({})".format(ch,my_run[run][ch]["Label"]).replace("#"," ")
            if len(keys) == 1:
                ave = my_run[run][ch][keys[counter]][0]
            elif len(keys) > 1:
                ave = my_run[run][ch][keys[counter]][0]
                counter = counter + 1
            norm_ave = np.max(ave)
            sampling = my_run[run][ch]["Sampling"] # To reset the sampling to its initial value (could be improved)
            thrld = 1e-6
            if check_key(OPT,"NORM") == True and OPT["NORM"] == True:
                ave = ave/norm_ave
            if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"]==True:
                fig.supxlabel(r'Time [$\mu$s]')
                sampling = my_run[run][ch]["Sampling"]*1e6
            if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                axs.semilogy()
            if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                ref_threshold = np.argmax(ave>np.max(ave)*2/3)
                if ref_max_idx == -1:
                    ref_max_idx = ref_threshold
                ave = shift(ave, ref_max_idx-ref_threshold, cval = 0)

            if check_key(OPT, "SCINT_FIT") == True and OPT["SCINT_FIT"]==True:
                fit, popt = fit_wvfs(my_run, "Scint", thrld, fit_range=[200,4000],sigma = 1e-8, a_fast = 1e-8, a_slow = 1e-6,OPT={"SHOW":False}, in_key=[keys[counter]])
                axs.plot(my_run[run][ch]["Sampling"]*np.arange(len(fit)),fit*norm_ave, linestyle="--", alpha = 0.95, linewidth=1.0, label = label+" (Fit)")
            
            axs.plot(sampling*np.arange(len(ave)),ave, drawstyle = "steps", alpha = 0.95, linewidth=1.2, label = label.replace("#"," "))

        axs.grid(True, alpha = 0.7)
        axs.set_title(title,size = 14)
        axs.xaxis.offsetText.set_fontsize(14) # Smaller fontsize for scientific notation
        if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
            axs.legend()
       
        tecla      = input("\nPress q to quit, p to save plot and any key to continue: ")
        if tecla   == "q":
            break 
        elif tecla == "p":
            fig.savefig('AveWvf_Ch{}.png'.format(ch), dpi = 500)
            ch = ch+1
        else:
            ch = ch+1
        if ch == len(ch_list): break
        try: [axs[ch].clear() for ch in range (nch)]
        except: axs.clear()
        plt.close()   

def vis_var_hist(my_run, key, compare = "NONE", percentile = [0.1, 99.9], OPT = {"SHOW": True}, select_range = False):
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

    figure_features()
    all_counts = []
    all_bins = []
    all_bars = []
    r_list = my_run["NRun"]
    ch_list = my_run["NChannel"]
    if compare == "CHANNELS":
        a_list = r_list 
        b_list = ch_list 
    if compare == "RUNS":
        a_list = ch_list 
        b_list = r_list
    if compare == "NONE":
        a_list = r_list
        b_list = ch_list
    data = []
    for a in a_list:
        if compare != "NONE": plt.ion(); fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)

        for b in b_list:
            if compare == "CHANNELS": run = a; ch = b; title = "Run_{} ".format(run); label = "{}".format(my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch)
            if compare == "RUNS":     run = b; ch = a; title = "{}".format(my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch); label = "Run {}".format(run)
            if compare == "NONE":     run = a; ch = b; title = "Run_{} - {}".format(run,my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch); label = ""
            if check_key(my_run[run][ch], "MyCuts") == False:
                generate_cut_array(my_run)
            if check_key(my_run[run][ch], "UnitsDict") == False:
                get_units(my_run)
            
            if compare == "NONE": plt.ion(); fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)
            for k in key:
                aux_data = my_run[run][ch][k][my_run[run][ch]["MyCuts"] == True]
                aux_data = aux_data[~np.isnan(aux_data)]
                if k == "PeakAmp":
                    data = aux_data
                    max_amp = np.max(data)
                    # binning = int(max_amp)+1
                    binning = 1000
                elif k == "PeakTime":
                    data = my_run[run][ch]["Sampling"]*aux_data
                    binning = int(my_run[run][ch]["NBinsWvf"]/10)
                else:
                    data = aux_data
                    ypbot = np.percentile(data, percentile[0]); yptop = np.percentile(data, percentile[1])
                    ypad = 0.2*(yptop - ypbot)
                    ymin = ypbot - ypad; ymax = yptop + ypad
                    data = [i for i in data if ymin<i<ymax]
                    binning = 400 # FIXED VALUE UNTIL BETTER SOLUTION
                
                if len(key) > 1:
                    fig.supxlabel(my_run[run][ch]["UnitsDict"][k]); fig.supylabel("Counts")
                    label = label + " - " + k
                    fig.suptitle(title)
                else:
                    fig.supxlabel(k+" ("+my_run[run][ch]["UnitsDict"][k]+")"); fig.supylabel("Counts")
                    fig.suptitle(title + " - {} histogram".format(k))

                if select_range:
                    x1 = float(input("xmin: ")); x2 = float(input("xmax: "))    
                    counts, bins, bars = ax.hist(data, bins = int(binning), label=label, histtype="step", range=(x1,x2)) # , zorder = 2 f
                else: counts, bins, bars = ax.hist(data,binning, label=label, histtype="step") # , zorder = 2 f
                label = label.replace(" - " + k,"")
                all_counts.append(counts)
                all_bins.append(bins)
                all_bars.append(bars)
            
            if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
                ax.legend()
            if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                ax.semilogy()
            if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True and compare == "NONE":
                plt.show()
                while not plt.waitforbuttonpress(-1): pass
                plt.close()
        if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True and compare != "NONE":
            plt.show()
            while not plt.waitforbuttonpress(-1): pass
            plt.close()
    return all_counts, all_bins, all_bars

def vis_two_var_hist(my_run, run, ch, keys, percentile = [0.1, 99.9], select_range = False, OPT={}):
    """
    This function plots two variables in a 2D histogram. Outliers are taken into account with the percentile. 
    It plots values below and above the indicated percetiles, but values are not removed from data.
    VARIABLES:
        - my_run: run(s) we want to check
        - keys: variables we want to plot as histograms. Type: List
        - percentile: percentile used for outliers removal
        - select_range: if we still have many outliers we can select the ranges in x and y axis.
    """
    figure_features()
    x_data = []; y_data = []

    if check_key(my_run[run][ch], "MyCuts") == False:
        generate_cut_array(my_run)
    if check_key(my_run[run][ch], "UnitsDict") == False:
        get_units(my_run)
    x_data = my_run[run][ch][keys[0]][my_run[run][ch]["MyCuts"] == True]; y_data = my_run[run][ch][keys[1]][my_run[run][ch]["MyCuts"] == True]

    #### Calculate range with percentiles for x-axis ####
    x_ypbot = np.percentile(x_data, percentile[0]); x_yptop = np.percentile(x_data, percentile[1])
    x_ypad = 0.2*(x_yptop - x_ypbot)
    x_ymin = x_ypbot - x_ypad; x_ymax = x_yptop + x_ypad
    #### Calculate range with percentiles for y-axis ####
    y_ypbot = np.percentile(y_data, percentile[0]); y_yptop = np.percentile(y_data, percentile[1])
    y_ypad = 0.2*(y_yptop - y_ypbot)
    y_ymin = y_ypbot - y_ypad; y_ymax = y_yptop + y_ypad
    plt.ion()
    fig, ax = plt.subplots(1,1, figsize = (8,6))
    if "Time" in keys[0]:
        ax.hist2d(x_data*my_run[run][ch]["Sampling"], y_data, bins=[600,600], range = [[x_ymin*my_run[run][ch]["Sampling"],x_ymax*my_run[run][ch]["Sampling"]],[y_ymin, y_ymax]], density=True, cmap = viridis, norm=LogNorm())
    else:
        ax.hist2d(x_data, y_data, bins=[600,600], range = [[x_ymin,x_ymax],[y_ymin, y_ymax]], density=True, cmap = viridis, norm=LogNorm())
    ax.grid("both")
    fig.supxlabel(keys[0]+" ("+my_run[run][ch]["UnitsDict"][keys[0]]+")"); fig.supylabel(keys[1]+" ("+my_run[run][ch]["UnitsDict"][keys[1]]+")")
    fig.suptitle("Run_{} Ch_{} - {} vs {} histogram".format(run,ch,keys[0],keys[1]))
    if select_range:
        x1 = float(input("xmin: ")); x2 = float(input("xmax: "))
        y1 = float(input("ymin: ")); y2 = float(input("ymax: "))
        ax.hist2d(x_data, y_data, bins=[300,300], range = [[x1,x2],[y1, y2]], density=True, cmap = viridis, norm=LogNorm())
        ax.grid("both")
        fig.supxlabel(keys[0]); fig.supylabel(keys[1])

    if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
        plt.yscale('log'); 
    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        plt.show()
        while not plt.waitforbuttonpress(-1): pass    
    return fig, ax