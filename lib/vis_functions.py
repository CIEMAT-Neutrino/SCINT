import matplotlib.pyplot as plt
import numpy as np

from .io_functions import load_npy,load_analysis_npy,load_average_npy,load_fit_npy
from .io_functions import check_key
from itertools import product

def vis_raw_npy(RUN,CH,OPT,KEY="ADC",PATH = "../data/raw/"):
    
    norm_raw = 1
    norm_ave = 1
    buffer = 100
    if KEY == "ADC":
        runs   = load_npy(RUN,CH)
    if KEY == "SC":
        runs   = load_fit_npy(RUN,CH)
    try:
        ana_runs = load_analysis_npy(RUN,CH)
        if check_key(OPT,"AVE") != False: AVE = OPT["AVE"]
        else: AVE = "AvWvf"
        try:
            ave_runs = load_average_npy(RUN,CH)
        except:
            print("Events have not been averaged")
    except:
        print("Events have not been processed")
    
    plt.ion()
    next_plot = False
    
    for run,ch in product(RUN,CH):
        for i in range(len(runs[run][ch][KEY])):
            
            plt.xlabel("Time in [s]")
            plt.ylabel("ADC Counts")
            if (KEY == "ADC"):
                min = np.argmin(runs[run][ch][KEY][i])
            if (KEY == "SC"):
                min = np.argmax(runs[run][ch][KEY][i])

            try:
                PED = ana_runs[run][ch]["Ped_mean"][i]    
                STD = ana_runs[run][ch]["Ped_STD"][i]

                if OPT["BASELINE"] == True:
                    if OPT["NORM"] == True:
                        norm_raw = np.max(ana_runs[run][ch]["P_channel"]*(np.array(runs[run][ch][KEY][i])-PED))      
                    plt.plot(np.arange(len(runs[run][ch][KEY][i]))*4e-9,ana_runs[run][ch]["P_channel"]*(np.array(runs[run][ch][KEY][i])-PED)/norm_raw,label="RAW_WVF")
                    try:
                        if OPT["NORM"] == True:
                            norm_ave = np.max(ave_runs[run][ch][AVE])
                        plt.plot(np.arange(len(runs[run][ch][KEY][i]))*4e-9,ave_runs[run][ch][AVE]/norm_ave,alpha = 0.5,label="AVE_WVF")
                    except:
                        print("Remember to run Average.py")
                    PED = 0
                
                else:
                    PED = np.mean(runs[run][ch][KEY][i][:min-buffer])
                    STD = np.std(runs[run][ch][KEY][i][:min-buffer])
                    
                    if OPT["NORM"] == True:
                        norm_raw = np.max(np.array(runs[run][ch][KEY][i]))      
                    plt.plot(np.arange(len(runs[run][ch][KEY][i]))*4e-9,np.array(runs[run][ch][KEY][i])/norm_raw,label="RAW_WVF")             
                
                if OPT["LOGY"] == True:
                    plt.semilogy()

            except:
                PED = np.mean(runs[run][ch][KEY][i][:min-buffer])
                STD = np.std(runs[run][ch][KEY][i][:min-buffer])
                plt.title("PED and Signal time evaluated at vis. time")
                plt.plot(np.arange(len(runs[run][ch][KEY][i]))*4e-9,np.array(runs[run][ch][KEY][i]))
                print("No PED nor POL information found to apply option.")

            plt.plot(4e-9*np.array([min-buffer,min-buffer]),np.array([PED+5*STD,PED-5*STD])/norm_raw,c="red",lw=2.)
            plt.axhline((PED)/norm_raw,c="k")
            plt.axhline((PED+STD)/norm_raw,c="k",alpha=0.5,ls="--")
            plt.axhline((PED-STD)/norm_raw,c="k",alpha=0.5,ls="--")
            plt.legend()

            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()