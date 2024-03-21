#================================================================================================================================================#
# In this library we have all the functions related with visualization. They are mostly used in 0XVis*.py macros but can be included anywhere !! #
#================================================================================================================================================#
from src.utils import get_project_root

import math, inquirer, yaml, os, stat
import numpy             as np
import matplotlib.pyplot as plt

from matplotlib.colors           import LogNorm
from matplotlib.cm               import viridis
from itertools                   import product
from scipy.signal                import find_peaks
from scipy.ndimage.interpolation import shift
from rich                        import print as rprint

# Imports from other libraries
from .io_functions  import check_key,print_colored
from .fig_config    import figure_features, add_grid
from .ana_functions import get_wvf_label,generate_cut_array,get_run_units
from .fit_functions import fit_wvfs
from .sty_functions import style_selector, get_prism_colors

root = get_project_root()

def vis_npy(my_run, info, keys, OPT = {}, save = False, debug = False):
    '''
    \nThis function is a event visualizer. It plots individual events of a run, indicating the pedestal level, pedestal std and the pedestal calc limit.
    \nWe can interact with the plot and pass through the events freely (go back, jump to a specific event...)
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- KEYS: choose between ADC or AnaADC to see raw (as get from ADC) or Analyzed events (starting in 0 counts), respectively. Type: List
    \n- OPT: several options that can be True or False. Type: List
      (a) MICRO_SEC: if True we multiply Sampling by 1e6.
      (b) NORM: True if we want normalized waveforms.
      (c) LOGY: True if we want logarithmic y-axis.
      (d) SHOW_AVE: if computed and True, it will show average.
      (e) SHOW_PARAM: True if we want to check calculated parameters (pedestal, amplitude, charge...).
      (f) CHARGE_KEY: if computed and True, it will show the parametre value.
      (g) PEAK_FINDER: True if we want to check how many peaks are.
      (h) CUTTED_WVF: choose the events we want to see. If -1 all events are displayed, if 0 only uncutted events are displayed, if 1 only cutted events are displayed.
      (i) SAME_PLOT: True if we want to plot different channels in the SAME plot.
    '''
    colors = get_prism_colors()
    if not check_key(OPT, "CUTTED_WVF"): OPT["CUTTED_WVF"] = -1; print_colored("CUTTED_WVF not defined, setting to -1", "WARNING")
    if not check_key(OPT, "SAME_PLOT"): OPT["SAME_PLOT"] = False; print_colored("SAME_PLOT not defined, setting to False", "WARNING")

    axs = []
    style_selector(OPT)
    ch_list = my_run["NChannel"]; nch = len(my_run["NChannel"])

    for run, key in product(my_run["NRun"],keys):
        plt.ion()
        if OPT["SAME_PLOT"] == False:
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
        if check_key(my_run[run][ch_list[0]], "MyCuts") == False: generate_cut_array(my_run, debug=debug)
        while idx < len(my_run[run][ch_list[0]]["MyCuts"]):
            try:
                skip = 0
                for ch in ch_list:
                    if OPT["CUTTED_WVF"] == 0 and my_run[run][ch]["MyCuts"][idx] == False: skip = 1; break # To Skip Cutted events!!
                    if OPT["CUTTED_WVF"] == 1 and my_run[run][ch]["MyCuts"][idx] == True:  skip = 1; break # To Get only Cutted events!!
                if skip == 1: idx = idx +1; continue
            except: pass

            fig.supxlabel(r'Time [s]')
            fig.supylabel("ADC Counts")
            raw = []
            norm_raw = [1]*nch # Generates a list with the norm correction for std bar
            
            for j in range(nch):
                if(key == "AnaADC"):
                    print_colored("\nAnaADC not saved but we compute it now :)", "WARNING")
                    label = "Ana"
                    ana = my_run[run][ch_list[j]]["PChannel"]*((my_run[run][ch_list[j]]["RawADC"][idx].T-my_run[run][ch_list[j]]["Raw"+info["PED_KEY"][0]][idx]).T)
                    raw.append(ana)
                    ped = 0
                    std = my_run[run][ch_list[j]]["AnaPedSTD"][idx]
                    if debug: print_colored("Using '%s' label"%label, "DEBUG")
                
                else:
                    label = key.split("ADC")[0]
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = my_run[run][ch_list[j]][label+info["PED_KEY"][0]][idx]
                    std = my_run[run][ch_list[j]][label+"PedSTD"][idx]
                    if debug: print_colored("Using '%s' label"%label, "DEBUG")

                if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
                    norm_raw[j] = (np.max(raw[j]))
                    raw[j] = raw[j]/np.max(raw[j])

                sampling = my_run[run][ch_list[j]]["Sampling"] # To reset the sampling to its initial value (could be improved)
                if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"]==True:
                    fig.supxlabel(r'Time [$\mu$s]')
                    my_run[run][ch_list[j]]["Sampling"] = my_run[run][ch_list[j]]["Sampling"]*1e6

                # if OPT["SAME_PLOT"] == False:
                if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                    axs[j].semilogy()
                    std = 0 # It is ugly if we see this line in log plots
                # fig.tight_layout(h_pad=2) # If we want more space betweeb subplots. We avoid small vertical space between plots            
                axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(raw[j])),raw[j],label="%s"%key, drawstyle = "steps", alpha = 0.95, linewidth=1.2, c=colors[0], zorder=0)
                try: axs[j].scatter(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"PeakTime"][idx],my_run[run][ch_list[j]][label+"PeakAmp"][idx], c=colors[1], zorder=10)
                except KeyError: print_colored("PeakAmp not computed!", "ERROR")    
                try: axs[j].scatter(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"ValleyTime"][idx],my_run[run][ch_list[j]][label+"ValleyAmp"][idx], c=colors[1], zorder=10)
                except KeyError: print_colored("ValleyAmp not computed!", "ERROR")    
                try: axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.array([my_run[run][ch_list[j]][label+"PedLim"],my_run[run][ch_list[j]][label+"PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw[j], lw=2, c=colors[6], zorder=3)
                except KeyError: print_colored("PedLim not computed!", "ERROR")    
                try:    
                    for value in ["PedStart", "PedEnd"]: axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.array([my_run[run][ch_list[j]][label+value][idx],my_run[run][ch_list[j]][label+value][idx]]),np.array([ped+4*std,ped-4*std])/norm_raw[j], lw=2, c=colors[4], zorder=3)
                except KeyError: print_colored("PedWindow not compued!", "ERROR")    
                try:
                    int_info = yaml.load(open(info["PATH"][0]+info["MONTH"][0]+"/npy/run"+str(run).zfill(2)+f"_ch{ch_list[j]}/ChargeDict.yml"), Loader=yaml.FullLoader)
                    for charge in int_info[OPT["CHARGE_KEY"]]:
                        for i in range(2): axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.array([int_info[OPT["CHARGE_KEY"]][charge][i],int_info[OPT["CHARGE_KEY"]][charge][i]]),np.array([ped+4*std,ped-4*std])/norm_raw[j], lw=2, c=colors[3], zorder=3)
                except FileNotFoundError: print("ChargeDict.yml not found!")
                axs[j].axhline((ped)/norm_raw[j],c="k",alpha=.55, zorder=2)
                axs[j].axhline((ped+std)/norm_raw[j],c="k",alpha=.5,ls="--", zorder=2); axs[j].axhline((ped-std)/norm_raw[j],c="k",alpha=.5,ls="--", zorder=2)
                axs[j].set_title("Run {} - Ch {} - Event Number {}".format(run,ch_list[j],idx),size = 14)
                axs[j].xaxis.offsetText.set_fontsize(14) # Smaller fontsize for scientific notation
                axs[j].grid(True, alpha = 0.7)
                
                if check_key(OPT, "SHOW_AVE") == True:   
                    try:
                        ave_key = label+OPT["SHOW_AVE"]
                        ave = my_run[run][ch_list[j]][ave_key][0]
                        if OPT["NORM"] == True and OPT["NORM"] == True:
                            ave = ave/np.max(ave)
                        if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                            ref_max_idx = np.argmax(raw[j])
                            idx_move = np.argmax(ave)
                            ave = shift(ave, ref_max_idx-idx_move, cval = 0)
                        axs[j].plot(my_run[run][ch_list[j]]["Sampling"]*np.arange(len(ave)),ave, label="%s"%ave_key, drawstyle = "steps", c=colors[5], alpha=.5, zorder=1)             
                    except KeyError: print_colored("Run has not been averaged!", "ERROR")

                if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]: axs[j].legend()

                if check_key(OPT, "PEAK_FINDER") == True and OPT["PEAK_FINDER"]:
                    # These parameters must be modified according to the run...
                    if check_key(my_run[run][ch_list[j]], "AveWvfSPE") == False: thresh = my_run[run][ch_list[j]]["PedMax"][idx] + 0.5*my_run[run][ch_list[j]]["PedMax"][idx]
                    else:                                                        thresh = np.max(my_run[run][ch_list[j]]["AveWvfSPE"])*3/4
                    
                    wdth = 4; prom = 0.01; dist  = 30
                    axs[j].axhline(thresh,c="k", alpha=.6, ls = "dotted")
                    peak_idx, _ = find_peaks(raw[j], height = thresh, width = wdth, prominence = prom, distance=dist)
                    for p in peak_idx: axs[j].scatter(my_run[run][ch_list[j]]["Sampling"]*p,raw[j][p],c=colors[7], alpha = 0.9)

                try:
                    if my_run[run][ch_list[j]]["MyCuts"][idx] == False:
                        figure_features(tex = False)
                        axs[j].text(0.5,0.5, s = 'CUT', fontsize = 100, horizontalalignment='center',verticalalignment='center',
                                    transform = axs[j].transAxes, color = 'red', fontweight = "bold", alpha = 0.5)
                        figure_features()
                except: pass
                    
                if check_key(OPT, "SHOW_PARAM") == True and OPT["SHOW_PARAM"]:
                    print_colored("\nEvent Number {} from RUN_{} CH_{} ({})".format(idx,run,ch_list[j],my_run[run][ch_list[j]]["Label"]), "white", styles=["bold"])
                    try: print("- Sampling:\t{:.0E}".format(sampling))
                    except KeyError: print_colored("Sampling not found!", color="ERROR")
                    try: print("- TimeStamp:\t{:.2E}".format(my_run[run][ch_list[j]]["TimeStamp"][idx]))
                    except KeyError: print_colored("TimeStamp not found!", color="ERROR") 
                    try: print("- Polarity:\t{}".format(my_run[run][ch_list[j]]["PChannel"]))
                    except KeyError: print_colored("Polarity not found!", color="ERROR")
                    print("\n--- PreTrigger ---")
                    try: print("- PreTrigger mean:\t{:.2E}".format(my_run[run][ch_list[j]][label+"PreTriggerMean"][idx]))
                    except KeyError: print_colored("PreTrigger mean not found!", color="ERROR")
                    try: print("- PreTrigger std:\t{:.4f}".format(my_run[run][ch_list[j]][label+"PreTriggerSTD"][idx]))
                    except KeyError: print_colored("PreTrigger std not found!", color="ERROR")
                    try: print("- PreTrigger min/max:\t{:.4f}/{:.4f}".format(my_run[run][ch_list[j]][label+"PreTriggerMin"][idx],my_run[run][ch_list[j]][label+"PreTriggerMax"][idx]))
                    except KeyError: print_colored("PreTrigger min/max not found!", color="ERROR")
                    try: print("- PreTrigger limit:\t{:.2E}".format(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"PedLim"]))
                    except KeyError: print_colored("PreTrigger time limit not found!", color="ERROR")
                    print("\n--- Pedestal from SlidingWindow Algorithm ---")
                    try: print("- S. Pedestal mean:\t{:.2E}".format(my_run[run][ch_list[j]][label+"PedMean"][idx]))
                    except KeyError: print_colored("Pedestal mean not found!", color="ERROR")
                    try: print("- S. Pedestal std:\t{:.4f}".format(my_run[run][ch_list[j]][label+"PedSTD"][idx]))
                    except KeyError: print_colored("Pedestal std not found!", color="ERROR")
                    try: print("- S. Pedestal min/max:\t{:.4f}/{:.4f}".format(my_run[run][ch_list[j]][label+"PedMin"][idx],my_run[run][ch_list[j]][label+"PedMax"][idx]))
                    except KeyError: print_colored("Pedestal min/max not found!", color="ERROR")
                    try: print("- S. Window start:\t{:.2E}".format(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"PedStart"][idx]))
                    except KeyError: print_colored("window start not found!", color="ERROR")
                    try: print("- S. Window stop:\t{:.2E}".format(my_run[run][ch_list[j]]["Sampling"]*my_run[run][ch_list[j]][label+"PedEnd"][idx]))
                    except KeyError: print_colored("window end not found!", color="ERROR")
                    print("\n--- Peak Variables ---")
                    try: print("- Max peak amplitude:\t{:.4f}".format(my_run[run][ch_list[j]][label+"PeakAmp"][idx]))
                    except KeyError: print_colored("Max peak amplitude not found!", color="ERROR")
                    try: print("- Max peak time:\t{:.2E}".format(my_run[run][ch_list[j]][label+"PeakTime"][idx]*my_run[run][ch_list[j]]["Sampling"]))
                    except KeyError: print_colored("Max peak time not found!", color="ERROR")
                    print("\n--- Valley Variables ---")
                    try: print("- Min valley amplitude:\t{:.4f}".format(my_run[run][ch_list[j]][label+"ValleyAmp"][idx]))
                    except KeyError: print_colored("Min valley amplitude not found!", color="ERROR")
                    try: print("- Min valley time:\t{:.2E}".format(my_run[run][ch_list[j]][label+"ValleyTime"][idx]*my_run[run][ch_list[j]]["Sampling"]))
                    except KeyError: print_colored("Min valley time not found!", color="ERROR")
                    try: print("- "+label+OPT["CHARGE_KEY"]+":\t{:.2E}".format(my_run[run][ch_list[j]][label+OPT["CHARGE_KEY"]][idx]))
                    except: print_colored("- Charge: %s has not been computed!"%(label+OPT["CHARGE_KEY"]), "WARNING")
                    try:print("- Peak_idx:",peak_idx*my_run[run][ch_list[j]]["Sampling"])
                    except:
                        if not check_key(OPT,"PEAK_FINDER"): print("")
                my_run[run][ch_list[j]]["Sampling"] = sampling    

            tecla = input("\nPress q to quit, p to save plot, r to go back, n to choose event or any key to continue: ")

            if   tecla == "q": break
            elif tecla == "r": idx = idx-1
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                idx = ev_num
                if idx > len(my_run[run][ch_list[j]]["MyCuts"]): idx = len(my_run[run][ch_list[j]]["MyCuts"])-1; print_colored("\nBe careful! There are %i in total"%idx, "WARNING", styles=["bold"])
            elif tecla == "p":
                fig.savefig(f'{root}{info["PATH"][0]}{info["MONTH"][0]}/images/run{run}_ch{ch}_event{idx}.png', dpi = 500)
                idx = idx+1
            else: idx = idx + 1
            if idx == len(my_run[run][ch_list[j]]["MyCuts"]): break
            try: [axs[j].clear() for j in range (nch)]
            except: axs.clear()
        try: [axs[j].clear() for j in range (nch)]
        except: axs.clear()
        plt.close()

def vis_compare_wvf(my_run, info, keys, OPT = {}, save = False, debug = False):
    '''
    \nThis function is a waveform visualizer. It plots the selected waveform with the key and allow comparisson between runs/channels.
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- KEYS: waveform to plot (AveWvf, AveWvdSPE, ...). Type: List
    \n- OPT: several options that can be True or False.  Type: List
      (a) MICRO_SEC: if True we multiply Sampling by 1e6
      (b) NORM: True if we want normalized waveforms
      (c) LOGY: True if we want logarithmic y-axis
    \n- compare: 
      (a) "RUNS" to get a plot for each channel and the selected runs. Type: String
      (b) "CHANNELS" to get a plot for each run and the selected channels. Type: String
    '''
    style_selector(OPT)
    r_list = my_run["NRun"]
    if type(r_list) != list:
        try: r_list = r_list.tolist()
        except: print_colored("Imported runs as list!", "INFO")
    ch_loaded = my_run["NChannel"]
    if type(ch_loaded) != list:
        try: ch_loaded = ch_loaded.tolist()
        except: print_colored("Imported channels as list!", "INFO")
    nch = len(my_run["NChannel"])
    axs = []
    
    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        # if len(ch_loaded) == 1: ch_loaded = [ch_loaded]
        q = [ inquirer.Checkbox("channels", message="Select channels to plot?", choices=ch_loaded, default=ch_loaded) ]
        ch_list =  inquirer.prompt(q)["channels"]
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False: ch_list = ch_loaded
    
    a_list = r_list
    b_list = ch_list
    if not check_key(OPT, "COMPARE"):OPT["COMPARE"] = "NONE"; print_colored("No comparison selected. Default is NONE", "WARNING")
    if OPT["COMPARE"] == "RUNS":     a_list = ch_list; b_list = r_list 
    if OPT["COMPARE"] == "CHANNELS": a_list = r_list;  b_list = ch_list 
    if OPT["COMPARE"] == "NONE":     a_list = r_list;  b_list = ch_list
    for a_idx, a in enumerate(a_list):
        if OPT["COMPARE"] == "RUNS":     ch = a
        if OPT["COMPARE"] == "CHANNELS": run = a
        if OPT["COMPARE"] == "NONE":     run = a; ch = b_list
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
            if OPT["COMPARE"] == "RUNS":
                run = b
                # label = "Run {} - {}".format(run,keys[counter]);title = "Average Waveform - Ch {}".format(ch)
            if OPT["COMPARE"] == "CHANNELS": 
                ch = b
                # label = "Channel {} ({}) - {}".format(ch,my_run[run][ch]["Label"],keys[counter]); title = "Average Waveform - Run {}".format(run)
            if OPT["COMPARE"] == "NONE":     run = a; ch = b
            for key in keys:
                if OPT["COMPARE"] == "NONE": label = "Run {} - Channel {} ({}) - {}".format(run,ch,my_run[run][ch]["Label"],key); title = "Average Waveform"
                if OPT["COMPARE"] == "RUNS": label = "Run {} - {}".format(run,key); title = "Average Waveform - Ch {}".format(ch)
                if OPT["COMPARE"] == "CHANNELS": label = "Channel {} ({}) - {}".format(ch,my_run[run][ch]["Label"],key); title = "Average Waveform - Run {}".format(run)
                ave = my_run[run][ch][key][0]
                counter = counter + 1

                norm_ave = np.max(ave)
                sampling = my_run[run][ch]["Sampling"] # To reset the sampling to its initial value (could be improved)
                thrld = 1e-6
                if check_key(OPT,"NORM") == True and OPT["NORM"] == True:
                    ave = ave/norm_ave
                    fig.supylabel("Norm")
                if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"]==True: fig.supxlabel(r'Time [$\mu$s]'); sampling = my_run[run][ch]["Sampling"]*1e6
                if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:         axs.semilogy()
                if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                    ref_threshold = np.argmax(ave>np.max(ave)*2/3)
                    if ref_max_idx == -1: ref_max_idx = ref_threshold
                    ave = np.roll(ave, ref_max_idx-ref_threshold)
                if check_key(OPT, "SPACE_OUT") and OPT["SPACE_OUT"] != 0:
                    # for each b in b_list, we want to plot the same waveform with a different offset in x
                    ave = np.roll(ave, int(b)*int(OPT["SPACE_OUT"]))
                axs.plot(sampling*np.arange(len(ave)),ave, drawstyle = "steps", alpha = 0.95, linewidth=1.2, label = label.replace("#"," "))

        axs.grid(True, alpha = 0.7)
        axs.set_title(title,size = 14)
        axs.xaxis.offsetText.set_fontsize(14) # Smaller fontsize for scientific notation
        if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]: axs.legend()
       
        tecla   = input("\nPress q to quit, p to save plot and any key to continue: ")
        counter = 0
        if tecla   == "q": break 
        elif tecla == "p": fig.savefig(f'{root}{info["PATH"][0]}{info["MONTH"][0]}/images/run{run}_ch{ch}_AveWvf.png', dpi = 500); counter += 1
        else: counter += 1
        if   counter > len(ch_list): break
        elif counter > len(r_list):  break
        try: [axs[ch].clear() for ch in range (nch)]
        except: axs.clear()
        plt.close()   

def vis_var_hist(my_run, info, key, percentile = [0.1, 99.9], OPT = {"SHOW": True}, select_range = False, save = False, debug = False):
    '''
    \nThis function takes the specified variables and makes histograms. The binning is fix to 600, so maybe it is not the appropriate.
    \nOutliers are taken into account with the percentile. It discards values below and above the indicated percetiles.
    \nIt returns values of counts, bins and bars from the histogram to be used in other function.
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- keys: variables we want to plot as histograms. Type: List
      (a) PeakAmp: histogram of max amplitudes of all events. The binning is 1 ADC. There are not outliers.
      (b) PeakTime: histogram of times of the max amplitude in events. The binning is the double of the sampling. There are not outliers.
      (c) Other variable: any other variable. Here we reject outliers.
    \n- percentile: percentile used for outliers removal
    \nWARNING! Maybe the binning stuff should be studied in more detail.
    '''
    style_selector(OPT)
    all_counts = []; all_bins = []; all_bars = []
    r_list = my_run["NRun"]; ch_loaded = my_run["NChannel"]
    if type(ch_loaded) != list:
        try: ch_loaded = ch_loaded.tolist()
        except: print_colored("Imported channels as list!", "INFO")

    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        q = [ inquirer.Checkbox("channels", message="Select channels to plot?", choices=ch_loaded, default=ch_loaded) ]
        ch_list =  inquirer.prompt(q)["channels"]
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False: ch_list = ch_loaded

    if not check_key(OPT, "COMPARE"): OPT["COMPARE"] = "NONE"; print_colored("No comparison selected. Default is NONE", "WARNING")
    if OPT["COMPARE"] == "CHANNELS": a_list = r_list;  b_list = ch_list 
    if OPT["COMPARE"] == "RUNS":     a_list = ch_list; b_list = r_list
    if OPT["COMPARE"] == "NONE":     a_list = r_list;  b_list = ch_list

    data = []
    for idx,a in enumerate(a_list):
        if OPT["COMPARE"] != "NONE":
            plt.ion()
            fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)

        for jdx,b in enumerate(b_list):
            if OPT["COMPARE"] == "RUNS":     run = b; ch = a; title = "{}".format(my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch); label = "Run {}".format(run)
            if OPT["COMPARE"] == "CHANNELS": run = a; ch = b; title = "Run_{} ".format(run); label = "{}".format(my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch)
            if OPT["COMPARE"] == "NONE":     run = a; ch = b; title = "Run_{} - {}".format(run,my_run[run][ch]["Label"]).replace("#"," ") + " (Ch {})".format(ch); label = ""
            if check_key(my_run[run][ch], "MyCuts") == False:    generate_cut_array(my_run,debug=True)
            if check_key(my_run[run][ch], "UnitsDict") == False: get_run_units(my_run)
            
            if OPT["COMPARE"] == "NONE": fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)
            
            binning = 0
            if check_key(OPT, "ACCURACY") == True: binning = OPT["ACCURACY"]

            for k in key:
                # Debug the following line
                if debug: print_colored("Plotting variable: %s"%k, color="INFO")
                aux_data = np.asarray(my_run[run][ch][k])[np.asarray(my_run[run][ch]["MyCuts"] == True)]
                aux_data = aux_data[~np.isnan(aux_data)]
                
                if k == "PeakAmp":
                    data = aux_data
                    if binning == 0: binning = 1000
                
                elif k == "PeakTime":
                    data = my_run[run][ch]["Sampling"]*aux_data
                    if binning == 0: binning = int(my_run[run][ch]["NBinsWvf"]/10)
                    
                else:
                    data = aux_data
                    ypbot = np.percentile(data, percentile[0]); yptop = np.percentile(data, percentile[1])
                    ypad = 0.2*(yptop - ypbot)
                    ymin = ypbot - ypad; ymax = yptop + ypad
                    data = [i for i in data if ymin < i < ymax]
                    if binning == 0: binning = 400 # FIXED VALUE UNTIL BETTER SOLUTION

                density = False
                y_label = "Counts"
                if check_key(OPT, "DENSITY") == True and OPT["DENSITY"] == True:
                    y_label = "Density"
                    density = True

                if select_range:
                    x1 = -1e6
                    while x1 == -1e6:
                        try:    x1 = float(input("xmin: ")); x2 = float(input("xmax: "))
                        except: x1 = -1e6 
                        counts, bins = np.histogram(data, bins = int(binning), range=(x1,x2), density=density)
                else: 
                    counts, bins = np.histogram(data, bins = int(binning), density=density)
                if check_key(OPT, "NORM") and OPT["NORM"]:
                    counts = counts/np.max(counts)   
                    y_label = "Norm (a.u.)"

                if len(key) > 1:
                    fig.supxlabel(my_run[run][ch]["UnitsDict"][k]);
                    fig.supylabel(y_label)
                    label = label + " - " + k
                    fig.suptitle(title)
                else:
                    fig.supxlabel(k+" ("+my_run[run][ch]["UnitsDict"][k]+")"); 
                    fig.supylabel(y_label)
                    fig.suptitle(title + " - {} histogram".format(k))

                colors = get_prism_colors()
                factor = 1
                if len(b_list) <= 4:
                    factor = 2
                ax.plot(bins[:-1], counts, drawstyle = "steps", label=label, alpha = 0.95, linewidth=1.2, c=colors[1+factor*(idx+jdx)])
                
                label = label.replace(" - " + k,"")
                all_counts.append(counts)
                all_bins.append(bins)
                # all_bars.append(bars)
            
            if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:        ax.legend()
            if check_key(OPT, "LOGY")   == True and OPT["LOGY"]  == True: ax.semilogy()
            if check_key(OPT, "STATS")  == True and OPT["STATS"] == True: print_stats(my_run,run,ch,ax,data)
            if check_key(OPT, "SHOW")   == True and OPT["SHOW"] == True and OPT["COMPARE"] == "NONE":
                plt.ion()
                plt.show()
                if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
                    while not plt.waitforbuttonpress(-1): pass
                    plt.close()
        if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True and OPT["COMPARE"] != "NONE":
            plt.show()
            if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
                while not plt.waitforbuttonpress(-1): pass
        if save: 
            fig.savefig(f'{root}{info["PATH"][0]}{info["MONTH"][0]}/images/run{run}_ch{ch}_{"_".join(key)}_Hist.png', dpi=500)
            if debug:
                rprint(f"Saved figure as: run{run}_ch{ch}_{'_'.join(key)}_Hist.png")
        plt.close()

    return all_counts, all_bins

def print_stats(my_run, run, ch, ax, data, save = False, debug = False):
    '''
    \nThis function prints the statistics of the data.
    '''
    times = np.asarray(my_run[run][ch]["TimeStamp"])[np.asarray(my_run[run][ch]["MyCuts"] == True)]
    rate = 1/np.mean(np.diff(times))
    print_colored("\nStatistics of the histogram:", "INFO")
    print_colored("- Counts: %i"%len(data), color="INFO")
    print_colored("- Rate: %.2E"%rate, color="INFO")
    print_colored("- Mean: {:.2E}".format(np.mean(data)), "INFO")
    print_colored("- Median: {:.2E}".format(np.median(data)), "INFO")
    print_colored("- Std: {:.2E}".format(np.std(data)), "INFO")

    # Add reference lines to the plot
    ax.axvline(np.mean(data), c="k", alpha=0.5)
    ax.axvline(np.mean(data)+np.std(data), c="k", ls="--", alpha=0.5)
    ax.axvline(np.mean(data)-np.std(data), c="k", ls="--", alpha=0.5)

def vis_two_var_hist(my_run, info, keys, percentile = [0.1, 99.9], select_range = False, OPT={}, save = False, debug = False):
    '''
    \nThis function plots two variables in a 2D histogram. Outliers are taken into account with the percentile. 
    \nIt plots values below and above the indicated percetiles, but values are not removed from data.
    \n**VARIABLES:**
    \n- my_run: run(s) we want to check
    \n- keys: variables we want to plot as histograms. Type: List
    \n- percentile: percentile used for outliers removal
    \n- select_range: if we still have many outliers we can select the ranges in x and y axis.
    '''
    style_selector(OPT)
    r_list = my_run["NRun"]; ch_loaded = my_run["NChannel"]
    if type(ch_loaded) != list:
        try: ch_loaded = ch_loaded.tolist()
        except: print_colored("Imported channels as list!", "INFO")
    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        q = [ inquirer.Checkbox("channels", message="Select channels to plot?", choices=ch_loaded, default=ch_loaded) ]
        ch_list =  inquirer.prompt(q)["channels"]
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False: ch_list = ch_loaded

    if not check_key(OPT, "COMPARE"): OPT["COMPARE"] = "NONE"; print_colored("No comparison selected. Default is NONE", "WARNING")
    if OPT["COMPARE"] == "CHANNELS": a_list = r_list;  b_list = ch_list 
    if OPT["COMPARE"] == "RUNS":     a_list = ch_list; b_list = r_list
    if OPT["COMPARE"] == "NONE":     a_list = r_list;  b_list = ch_list

    x_data = []; y_data = []
    for run in r_list:
        for ch in ch_list:
            if check_key(my_run[run][ch], "MyCuts") == False:    generate_cut_array(my_run)
            if check_key(my_run[run][ch], "UnitsDict") == False: get_run_units(my_run)
    figures_list = []
    axes_list = []
    for a in a_list:
        for b in b_list:
            fig, ax = plt.subplots(1,1, figsize = (8,6)); add_grid(ax)

            if OPT["COMPARE"] == "CHANNELS": 
                title = "Run_{} ".format(a);
                label0 = "{}".format(my_run[a][ch_list[0]]["Label"]).replace("#","")
                label1 = "{}".format(my_run[a][ch_list[1]]["Label"]).replace("#","")
                aux_x_data = my_run[a][ch_list[0]][keys[0]][my_run[a][ch_list[0]]["MyCuts"] == True]; aux_y_data = my_run[a][ch_list[1]][keys[1]][my_run[a][ch_list[1]]["MyCuts"] == True]
            if OPT["COMPARE"] == "RUNS":
                title = "Channel_{} ".format(a);
                label0 = "{}".format(my_run[r_list[0]][a]["Label"]).replace("#","")
                label1 = "{}".format(my_run[r_list[1]][a]["Label"]).replace("#","")
                aux_x_data = my_run[r_list[0]][a][keys[0]][my_run[r_list[0]][a]["MyCuts"] == True]; aux_y_data = my_run[r_list[1]][a][keys[1]][my_run[r_list[1]][a]["MyCuts"] == True]
            if OPT["COMPARE"] == "NONE":
                title = "Run_{} Ch_{} - {} vs {} histogram".format(a,b,keys[0],keys[1])
                label0 = ""; label1 = ""
                aux_x_data = my_run[a][b][keys[0]][my_run[a][b]["MyCuts"] == True]; aux_y_data = my_run[a][b][keys[1]][my_run[a][b]["MyCuts"] == True]

            aux_x_data = aux_x_data[~np.isnan(aux_x_data)]; aux_y_data = aux_y_data[~np.isnan(aux_y_data)]
            x_data = aux_x_data; y_data = aux_y_data
            
            #### Calculate range with percentiles for x-axis ####
            x_ypbot = np.percentile(x_data, percentile[0]); x_yptop = np.percentile(x_data, percentile[1])
            x_ypad = 0.2*(x_yptop - x_ypbot)
            x_ymin = x_ypbot - x_ypad; x_ymax = x_yptop + x_ypad
            
            #### Calculate range with percentiles for y-axis ####
            y_ypbot = np.percentile(y_data, percentile[0]); y_yptop = np.percentile(y_data, percentile[1])
            y_ypad = 0.2*(y_yptop - y_ypbot)
            y_ymin = y_ypbot - y_ypad; y_ymax = y_yptop + y_ypad

            if "Time" in keys[0]:
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True: hist = ax.hist2d(x_data*my_run[run][ch]["Sampling"], y_data, bins=[600,600], range = [[x_ymin*my_run[run][ch]["Sampling"],x_ymax*my_run[run][ch]["Sampling"]],[y_ymin, y_ymax]], cmap = viridis, norm=LogNorm())
                else: hist = ax.hist2d(x_data*my_run[run][ch]["Sampling"], y_data, bins=[600,600], range = [[x_ymin*my_run[run][ch]["Sampling"],x_ymax*my_run[run][ch]["Sampling"]],[y_ymin, y_ymax]], cmap = viridis)
                plt.colorbar(hist[3])
            else:
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True: hist = ax.hist2d(x_data, y_data, bins=[600,600], range = [[x_ymin,x_ymax],[y_ymin, y_ymax]], cmap = viridis, norm=LogNorm())
                else: hist = ax.hist2d(x_data, y_data, bins=[600,600], range = [[x_ymin,x_ymax],[y_ymin, y_ymax]], cmap = viridis)
                plt.colorbar(hist[3])
            
            ax.grid("both")
            fig.supxlabel(label0 + " " + keys[0]+" ("+my_run[run][ch]["UnitsDict"][keys[0]]+")"); fig.supylabel(label1 + " " + keys[1]+" ("+my_run[run][ch]["UnitsDict"][keys[1]]+")")
            fig.suptitle(title)
            if select_range:
                x1 = -1e6
                while x1 == -1e6:
                    try:
                        x1 = float(input("xmin: ")); x2 = float(input("xmax: "))
                        y1 = float(input("ymin: ")); y2 = float(input("ymax: "))
                    except:
                        x1 = -1e6
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True: hist = ax.hist2d(x_data, y_data, bins=[300,300], range = [[x1,x2],[y1, y2]], cmap = viridis, norm=LogNorm())
                else: hist = ax.hist2d(x_data, y_data, bins=[300,300], range = [[x1,x2],[y1, y2]], cmap = viridis)  
                plt.colorbar(hist[3])
                ax.grid("both")

            figures_list.append(fig)
            axes_list.append(ax)
            if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.yscale('log'); 
            if save == True: 
                fig.savefig(f'{root}{info["PATH"][0]}{info["MONTH"][0]}/images/run{run}_ch{ch}_{title}_{keys[0]}_vs_{keys[1]}.png', dpi = 500)
                os.chmod(f'{root}{info["PATH"][0]}{info["MONTH"][0]}/images/run{run}_ch{ch}_{title}_{keys[0]}_vs_{keys[1]}.png', stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                if debug: rprint(f"Saved figure as: run{run}_ch{ch}_{title}_{keys[0]}_vs_{keys[1]}.png")
            
            # Save to specific folder determined by OPT
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True: 
                plt.ion()
                plt.show()
                while not plt.waitforbuttonpress(-1): pass
                plt.close()
            if OPT["COMPARE"] != "NONE": break

    return figures_list, axes_list