import matplotlib.pyplot as plt
import numpy as np

from .my_functions import load_npy
from .my_functions import load_analysis_npy
from .my_functions import load_average_npy
from pynput import keyboard
from itertools import product


def vis_raw_npy(RUN,CH,POL,OPT):
    
    buffer = 40
    runs   = load_npy(RUN,CH,POL)

    try:
        ana_runs = load_analysis_npy(RUN,CH,POL)
    except:
        print("Events have not been processed")
    
    try:
        ave_runs = load_average_npy(RUN,CH,POL)
    except:
        print("Events have not been averaged")
    
    
    plt.ion()
    next_plot = False
    
    for run,ch in product(RUN,CH):
        for i in range(len(runs[run][ch]["ADC"])):
            plt.xlabel("Time in [s]")
            plt.ylabel("ADC Counts")
            min = np.argmin(runs[run][ch]["ADC"][i])
            
            try:
                PED = ana_runs[run][ch]["Ped_mean"][i]    
                STD = ana_runs[run][ch]["Ped_STD"][i]    
                if OPT["BASELINE"] == True:
                    plt.plot(np.arange(len(runs[run][ch]["ADC"][i]))*4e-9,POL[ch]*(np.array(runs[run][ch]["ADC"][i])-PED))
                    plt.plot(np.arange(len(runs[run][ch]["ADC"][i]))*4e-9,ave_runs[run][ch]["ADC"],alpha = 0.5)
                    PED = 0
                
                if OPT["LOGY"] == True:
                    plt.semilogy()

            except:
                PED = np.mean(runs[run][ch]["ADC"][i][:min-buffer])
                STD = np.std(runs[run][ch]["ADC"][i][:min-buffer])
                plt.title("PED and Signal time evaluated at vis. time")
                plt.plot(np.arange(len(runs[run][ch]["ADC"][i]))*4e-9,np.array(runs[run][ch]["ADC"][i]))
                print("No PED nor POL information found to apply option.")
            
            # plt.axhline(len(runs[run][ch]["Pedestal"]),c="red")
            plt.plot(4e-9*np.array([min-buffer,min-buffer]),[PED+5*STD,PED-5*STD],c="red",lw=2.)
            plt.axhline(PED,c="k")
            plt.axhline(PED+STD,c="k",alpha=0.5,ls="--")
            plt.axhline(PED-STD,c="k",alpha=0.5,ls="--")

            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()