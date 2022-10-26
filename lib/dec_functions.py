import numpy as np
import matplotlib.pyplot as plt
from .my_functions import load_analysis_npy

from itertools import product

def gauss(X,STD,MEAN=0,NORM=1,N=2):
    A=1
    if NORM=="standard":
        A=1/(STD*np.sqrt(2*np.pi))
    else:
        A=NORM
    Y=A*np.exp(-(X-MEAN)**N/(2*STD**N))
    return Y

def deconvolve(my_runs,KERNEL,FS,TRIMM,OPT,PATH = "../data/dec/"):
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("Events have not been processed")

    KERNEL = KERNEL[:-TRIMM]

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        for i in range(len(my_runs[run][ch]["ADC"])):
            RAW = my_runs [run][ch]["ADC"][i]
            PED = ana_runs[run][ch]["Ped_mean"][i]    
            STD = ana_runs[run][ch]["Ped_STD"][i]
            POL = ana_runs[run][ch]["P_channel"]

            SIGNAL = POL*(RAW[:-TRIMM]-PED)
            
            while np.argmax(SIGNAL) < np.argmax(KERNEL):
                SIGNAL = np.roll(SIGNAL,1)    
            
            FFT_SIGNAL = np.fft.rfft(SIGNAL)
            FFT_KERNEL = np.fft.rfft(KERNEL)
            GAUSS_SIGNAL = FFT_SIGNAL*gauss(np.arange(len(FFT_SIGNAL)),FS)
            DEC = np.fft.irfft(GAUSS_SIGNAL/np.array(FFT_KERNEL/np.max(FFT_KERNEL)))
            DEC = np.roll(DEC,np.argmax(KERNEL))
            plt.plot(np.arange(len(SIGNAL))*4e-9,SIGNAL,label = "SIGNAL")
            # plt.plot(np.arange(len(KERNEL))*4e-9,KERNEL,label = "KERNEL")
            # plt.plot(np.arange(len(np.fft.irfft(GAUSS_SIGNAL)))*4e-9,np.fft.irfft(GAUSS_SIGNAL), label = "GAUSS_SIGNAL")
            plt.plot(np.arange(len(DEC))*4e-9,DEC,label="DECONVOLUTION")
            plt.legend()
            plt.show()