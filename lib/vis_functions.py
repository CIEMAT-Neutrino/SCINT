import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
import keyboard

from .io_functions import load_npy,check_key
from itertools import product

def vis_npy(my_run,KEYS,OPT):
    
    norm_raw = 1
    norm_ave = 1
    buffer = 100

    plt.ion()
    next_plot = False

    for run, ch, key in product(my_run["N_runs"],my_run["N_channels"],KEYS):
        counter = 0

        for i in range(len(my_run[run][ch]["Ana_ADC"])):
            plt.xlabel("Time in [s]")
            plt.ylabel("ADC Counts")
            plt.grid(True, alpha = 0.7)
            
            if (key == "ADC"):
                min = np.argmin(my_run[run][ch][key][counter])
                RAW = my_run[run][ch][key][counter]
                PED = np.mean(my_run[run][ch][key][counter][:min-buffer])
                STD = np.std(my_run[run][ch][key][counter][:min-buffer])
            
            elif(key == "Ana_ADC"):
                min = np.argmax(my_run[run][ch][key][counter])
                RAW = my_run[run][ch][key][counter]
                PED = 0    
                STD = my_run[run][ch]["Ped_STD"][counter]

            if OPT["NORM"] == True and OPT["NORM"] == True:
                norm_raw = np.max(RAW)
                RAW = RAW/np.max(RAW)
            plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(RAW)),RAW,label="RAW_WVF", drawstyle = "steps", alpha = 0.9)

            if check_key(OPT, "SHOW_AVE") == True:   
                try:
                    AVE_KEY = OPT["SHOW_AVE"]
                    AVE = my_run[run][ch][AVE_KEY][0]
                    if OPT["NORM"] == True and OPT["NORM"] == True:
                        AVE = AVE/np.max(AVE)
                    plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(AVE)),AVE,alpha=.5,label="AVE_WVF_%s"%AVE_KEY)             
                except:
                    print("Run has not been averaged!")
                        
            if OPT["LOGY"] == True:
                plt.semilogy()

            plt.plot(my_run[run][ch]["Sampling"]*np.array([min-buffer,min-buffer]),np.array([PED+5*STD,PED-5*STD])/norm_raw,c="red",lw=2., alpha = 0.8)
            plt.title("Run_{} Ch_{} - Event Number {}".format(run,ch,counter),size = 14)
            plt.axhline((PED)/norm_raw,c="k",alpha=.5)
            plt.axhline((PED+STD)/norm_raw,c="k",alpha=.5,ls="--"); plt.axhline((PED-STD)/norm_raw,c="k",alpha=.5,ls="--")
            plt.legend()

            if OPT["SHOW_PARAM"] == True:
                print("Event Number {} from RUN_{} CH_{} ({})".format(counter,run,ch,my_run[run][ch]["Label"]))
                print("Sampling: {:.0E}".format(my_run[run][ch]["Sampling"]))
                print("Pedestal mean: {:.2E}".format(my_run[run][ch]["Ped_mean"][counter]))
                print("Pedestal STD: {:.4f}".format(my_run[run][ch]["Ped_STD"][counter]))
                print("Pedestal min: {:.4f}\t Pedestal max {:.4f}".format(my_run[run][ch]["Ped_min"][counter],my_run[run][ch]["Ped_max"][counter]))
                print("Pedestal time limit: {:.4E}".format(4e-9*(min-buffer)))
                print("Max Peak Amplitude: {:.4f}".format(my_run[run][ch]["Peak_amp"][counter]))
                print("Max Peak Time: {:.2E}".format(my_run[run][ch]["Peak_time"][counter]*my_run[run][ch]["Sampling"]))
                print("Charge: {:.2E}\n".format(my_run[run][ch]["AVE_INT_LIMITS"][counter]))

            tecla = input("Press q to quit, r to go back, n to choose event or any key to continue: ")
            if tecla == "q":
                break
            elif tecla == "r":
                counter = counter-1
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                counter = ev_num
                if counter > len(my_run[run][ch]["Ana_ADC"]): counter = len(my_run[run][ch]["Ana_ADC"])-1
            else:
                counter = counter + 1
                # while not plt.waitforbuttonpress(-1): pass           
            if counter == len(my_run[run][ch]["Ana_ADC"]): break
            plt.clf()
        plt.clf()
    plt.ioff()
    plt.clf()

def vis_var_hist(my_run,KEY,w=1e-4,OPT={}): # Histogram visualizer
    # KEY is the variable that we want to plot
    # w is related to the bin width
    plt.ion()
    COUNTS = []
    BINS = []
    BARS = []
    for run, ch, key in product(my_run["N_runs"],my_run["N_channels"],KEY):
        # w = abs(np.max(my_run[run][ch][key])-np.min(my_run[run][ch][key]))*w
        data = []
        if key == "Peak_amp":
            data = my_run[run][ch][key]
            max_amp = np.max(data)
            binning = int(max_amp)+1
        elif key == "Peak_time":
            data = my_run[run][ch]["Sampling"]*my_run[run][ch][key]
            binning = int(my_run[run][ch]["NBins_wvf"]/2)
        else:
            data = my_run[run][ch][key]
            ypbot = np.percentile(data, 0.1); yptop = np.percentile(data, 99.9)
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
        COUNTS.append(counts)
        BINS.append(bins)
        BARS.append(bars)
        plt.grid(True, alpha = 0.7) # , zorder = 0 for grid behind hist
        plt.title("Run_{} Ch_{} - {} histogram".format(run,ch,key),size = 14)
        plt.xticks(size = 11); plt.yticks(size = 11)
        plt.xlabel(key+" (Units)", size = 11); plt.ylabel("Counts", size = 11)
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    plt.ioff()
    return COUNTS, BINS, BARS