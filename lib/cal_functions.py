import numpy as np
# import copy
# import sys

import scipy
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt

from itertools import product
from .io_functions import check_key
from .fit_functions import gaussian,loggaussian,gaussian_train,loggaussian_train

def calibrate(my_runs,KEY,OPT={}):
    """Computes calibration hist of a collection of runs and returns gain and SPE charge limits"""
    
    plt.ion()
    next_plot = False
    
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:

            raw_array = []
            raw_amp = []
            max_charge = 0 
            min_charge = 0

            for i in range(len(my_runs[run][ch][KEY])):
                thischarge = my_runs[run][ch][KEY][i]
                thisamp = my_runs[run][ch]["Peak_amp"][i]
                raw_array.append(thischarge)
                raw_amp.append(thisamp)

            mean = np.mean(raw_array)
            mode = raw_array[int(len(raw_array)/2)]
            std = np.std(raw_array)
            array = []

            for i in range(len(raw_array)):
                if abs(raw_array[i]-mean) < mean+10*std:
                    array.append(raw_array[i])
            # print(len(array))
            # print(array)
            # Threshold value (for height of peaks and valleys)
            binning = int(len(array)/100)
            thresh = int(len(array)/1000)
            wdth = 8
            prom = 0.1
            acc = 1000

            # counts, bins, bars = plt.hist(array,1000,alpha=0.75)
            # plt.show()

            counts, bins, bars = plt.hist(array,binning,(np.min(array)*0.5,np.max(array)),alpha=0.75)
            plt.xlabel("Charge in [ADC x ns]");plt.ylabel("Counts")
            for i in range(len(counts)):
                if counts[i] > thresh and bins[i] > max_charge:
                    max_charge = bins[i]
                    # print(max_charge)
                elif counts[i] > thresh and bins[i] < min_charge:
                    min_charge = bins[i]
                    # print(min_charge)

            x = np.linspace(min_charge,max_charge,acc)
            y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
            y = y_intrp(x)

            # Find indices of peaks
            peak_idx, _ = find_peaks(np.log10(y), height=np.log10(thresh), width=wdth, prominence=prom)

            # Find indices of valleys (from inverting the signal)
            valley_idx, _ = find_peaks(-np.log10(y), height=[-np.max(np.log10(counts)),-np.log10(thresh)], width=wdth, prominence=prom)

            # Plot threshold
            plt.axhline(thresh, ls='--')

            # Plot peaks (red) and valleys (blue)
            plt.plot(x[peak_idx], y[peak_idx], 'r.',lw=4)
            plt.plot(x[valley_idx], y[valley_idx], 'b.',lw=4)

            height,center,width = [],[],[]
            initial = []
            
            n_peaks = 6
            if len(peak_idx)-1 < n_peaks:
                n_peaks = len(peak_idx)-1
            
            for i in range(n_peaks):
                x_space = np.linspace(x[peak_idx[i]],x[peak_idx[i+1]],acc)
                step = x_space[1]-x_space[0]
                x_gauss = x_space-int(acc/2)*step
                x_gauss = x_gauss[x_gauss >= bins[0]]
                y_gauss = y_intrp(x_gauss)
                # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.5)

                try:
                    # popt, pcov = curve_fit(loggaussian,x_gauss,np.log10(y_gauss),p0=[np.log10(y[peak_idx[i]]),x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
                    popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[peak_idx[i]],x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
                    # height.append(popt[0])
                    # center.append(popt[1])
                    # width.append(popt[2])
                    initial.append(popt[1])
                    initial.append(popt[0])
                    initial.append(popt[2])
                    # plt.plot(x_gauss,gaussian(x_gauss,*popt),ls="--",c="black",alpha=0.5,label="Gaussian fit %i"%i)
                    plt.plot(x_gauss,gaussian(x_gauss,*popt),ls="--",c="black",alpha=0.5)
                
                except:
                    initial.append(x[peak_idx[i]])
                    initial.append(y[peak_idx[i]])
                    initial.append(abs(wdth*(bins[0]-bins[1])))
                    print("Peak %i could not be fitted"%i)

            try:
                # popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
                popt, pcov = curve_fit(gaussian_train,x[:peak_idx[-1]],y[:peak_idx[-1]],p0=initial)
            except:
                popt = initial
                print("Full fit could not be performed")
            plt.plot(x[:peak_idx[-1]],gaussian_train(x[:peak_idx[-1]],*popt),label="")

            # plt.legend()
            if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
                plt.semilogy()
            
            plt.ylim(thresh*0.9,np.max(counts)*1.1)
            plt.xlim(x[peak_idx[0]]-abs(wdth*(bins[0]-bins[1])),x[peak_idx[-1]]*1.1)
            
            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

            my_runs[run][ch]["Gain"] = popt[3]-abs(popt[0])
            my_runs[run][ch]["SPE_max_charge"] = popt[3] + abs(popt[5])
            print("SPE gauss parameters %.2E, %.2E, %.2E"%(popt[3],popt[4],popt[5]))
            # print("SPE max charge for run %i ch %i = %.2E"%(run,ch,popt[3] + abs(popt[5])))
            my_runs[run][ch]["SPE_min_charge"] = popt[3] - abs(popt[5])
            # print("SPE min charge for run %i ch %i = %.2E"%(run,ch,popt[3] - abs(popt[5])))

    plt.ioff()
    plt.clf()
