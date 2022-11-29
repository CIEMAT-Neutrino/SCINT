import sys
sys.path.insert(0, '../')

import matplotlib.pyplot as plt
import numpy as np
import keyboard

from .io_functions import load_npy,check_key
from itertools import product


def persistence_npy(my_run, keys, OPT):
    charge_key = "ChargeAveRange"
    if check_key(OPT, "CHARGE_KEY"): charge_key = OPT["CHARGE_KEY"]
    norm_raw = 1
    norm_ave = 1
    buffer = 100

    plt.ion()
    next_plot = False


    for run, ch, key in product(my_run["NRun"],my_run["NChannel"],keys):
        raw = my_run[run][ch][key][0]
        plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(raw)),raw,label="RAW_WVF", drawstyle = "steps", alpha = 0.9)
    #     idx = 0

    #     # for i in range(len(my_run[run][ch]["AnaADC"])):
    #     plt.xlabel("Time in [s]")
    #     plt.ylabel("ADC Counts")
    #     plt.grid(True, alpha = 0.7)
        
    #     if (key == "ADC"):
    #         min = np.argmin(my_run[run][ch][key][:2])
    #         RAW = my_run[run][ch][key][:]
    #         PED = np.mean(my_run[run][ch][key][:2][:min-buffer])
    #         STD = np.std(my_run[run][ch][key][:2][:min-buffer])
    #         COL = "tab:blue"

    #     elif(key == "Ana_ADC"):
    #         RAW = my_run[run][ch][key][:]
    #         PED = 0    
    #         STD = my_run[run][ch]["Ped_STD"][:]
    #         COL = "tab:green"
    #         raw = my_run[run][ch][key][:]
    #         ped = np.mean(my_run[run][ch][key][:2][:min-buffer])
    #         std = np.std(my_run[run][ch][key][:2][:min-buffer])
        
    #     elif(key == "AnaADC"):
    #         min = np.argmax(my_run[run][ch][key][:2])
    #         raw = my_run[run][ch][key][:]
    #         ped = 0    
    #         std = my_run[run][ch]["PedSTD"][:]

    #     if OPT["NORM"] == True and OPT["NORM"] == True:
    #         norm_raw = np.max(raw)
    #         raw = raw/np.max(raw)
        
    #     plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(raw)),raw,label="RAW_WVF", drawstyle = "steps", alpha = 0.9)
    #     plt.plot(my_run[run][ch]["Sampling"]*np.array([my_run[run][ch]["PedLim"],my_run[run][ch]["PedLim"]]),np.array([ped+4*std,ped-4*std])/norm_raw,c="red",lw=2., alpha = 0.8)

    #     if check_key(OPT, "SHOW_AVE") == True:   
    #         try:
    #             ave_key = OPT["SHOW_AVE"]
    #             ave = my_run[run][ch][ave_key][0]
    #             if OPT["NORM"] == True and OPT["NORM"] == True:
    #                 ave = ave/np.max(ave)
    #             plt.plot(my_run[run][ch]["Sampling"]*np.arange(len(ave)),ave,alpha=.5,label="AVE_WVF_%s"%ave_key)             
    #         except:
    #             print("Run has not been averaged!")
                    
    #     if OPT["LOGY"] == True:
    #         plt.semilogy()

    #     plt.title("Run_{} Ch_{} - Event Number {}".format(run,ch,idx),size = 14)
    #     plt.axhline((ped)/norm_raw,c="k",alpha=.5)
    #     plt.axhline((ped+std)/norm_raw,c="k",alpha=.5,ls="--"); plt.axhline((ped-std)/norm_raw,c="k",alpha=.5,ls="--")
    #     plt.legend()

    #     if OPT["SHOW_PARAM"] == True:
    #         print("Event Number {} from RUN_{} CH_{} ({})".format(idx,run,ch,my_run[run][ch]["Label"]))
    #         print("- Sampling: {:.0E}".format(my_run[run][ch]["Sampling"]))
    #         print("- Pedestal mean: {:.2E}".format(my_run[run][ch]["PedMean"][idx]))
    #         print("- Pedestal std: {:.4f}".format(my_run[run][ch]["PedSTD"][idx]))
    #         print("- Pedestal min: {:.4f}\t Pedestal max {:.4f}".format(my_run[run][ch]["PedMin"][idx],my_run[run][ch]["PedMax"][idx]))
    #         print("- Pedestal time limit: {:.4E}".format(my_run[run][ch]["Sampling"]*my_run[run][ch]["PedLim"]))
    #         print("- Max Peak Amplitude: {:.4f}".format(my_run[run][ch]["PeakAmp"][idx]))
    #         print("- Max Peak Time: {:.2E}".format(my_run[run][ch]["PeakTime"][idx]*my_run[run][ch]["Sampling"]))
    #         try:
    #             print("- Charge: {:.2E}\n".format(my_run[run][ch][OPT["CHARGE_KEY"]][idx]))
    #         except:
    #             if check_key(OPT,"CHARGE_KEY"): print("- Charge: has not been computed for key %s!"%OPT["CHARGE_KEY"])
    #             else: print("- Charge: defualt charge key has not been computed")

    #     tecla = input("\nPress q to quit, r to go back, n to choose event or any key to continue: ")
    #     if tecla == "q":
    #         break
        # elif tecla == "r":
        #     idx = idx-1
        # elif tecla == "n":
        #     ev_num = int(input("Enter event number: "))
        #     idx = ev_num
        #     if idx > len(my_run[run][ch]["AnaADC"]): idx = len(my_run[run][ch]["AnaADC"])-1
        # else:
        #     idx = idx + 1
        #     # while not plt.waitforbuttonpress(-1): pass           
        # if idx == len(my_run[run][ch]["AnaADC"]): break
        plt.clf()
    plt.clf()
    plt.ioff()
    plt.clf()