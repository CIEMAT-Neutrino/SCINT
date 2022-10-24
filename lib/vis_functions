import matplotlib.pyplot as plt
import numpy as np

from .my_functions import load_npy
from pynput import keyboard
from itertools import product


def vis_raw_npy(RUN,CH,POL,OPT,PATH = ""):

    runs=load_npy(RUN,CH,POL,PATH)
    buffer = 20
    
    plt.ion()
    next_plot = False

    for run,ch in product(RUN,CH):
        for i in range(len(runs[run][ch]["ADC"])):
            min = np.argmin(runs[run][ch]["ADC"][i])
            try:
                PED = runs[run][ch]["Ped_mean"][i]    
                STD = runs[run][ch]["Ped_STD"][i]    
            except:
                PED = np.mean(runs[run][ch]["ADC"][i][:min-buffer])
                STD = np.std(runs[run][ch]["ADC"][i][:min-buffer])
                plt.title("PED and Signal time evaluated at vis. time")
            
            plt.xlabel("Time in [s]")
            plt.ylabel("ADC Counts")
            
            if OPT[0] == True:
                try:
                    plt.plot(np.arange(len(runs[run][ch]["ADC"][i]))*4e-9,np.array(runs[run][ch]["ADC"][i]))
                except:
                    plt.plot(np.arange(len(runs[run][ch]["ADC"][i]))*4e-9,np.array(runs[run][ch]["ADC"][i]))
                    print("No PED nor POL information found to apply option.")
            try:
                # plt.axhline(len(runs[run][ch]["Pedestal"]),c="red")
                plt.plot(4e-9*np.array([min-buffer,min-buffer]),[PED+5*STD,PED-5*STD],c="green")
                plt.axhline(PED,c="red")
                plt.axhline(PED+STD,c="k",alpha=0.5,ls="--")
                plt.axhline(PED-STD,c="k",alpha=0.5,ls="--")
                if OPT[2] == True:
                    plt.logy()
            except:
                print("Unprocessed WVFs. Run Processing.py to obtain pedestal information.")
            
            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()