import sys
sys.path.insert(0, '../')

import scipy
import numpy as np
import matplotlib.pyplot as plt
from lib.io_functions import load_npy,load_analysis_npy,load_average_npy
from lib.fit_functions import gaussian,loggaussian, gaussian_train, loggaussian_train
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

RUN = 2
CH = 0
RUNS = load_analysis_npy([RUN],[CH])
print(len(RUNS[RUN][CH]["AVE_INT_LIMITS"]))
raw_array = []
max_charge = 0 
min_charge = 0

for i in range(len(RUNS[RUN][CH]["AVE_INT_LIMITS"])):
    thischarge = RUNS[RUN][CH]["AVE_INT_LIMITS"][i]
    raw_array.append(thischarge)

mean = np.mean(raw_array)
mode = raw_array[int(len(raw_array)/2)]
std = np.std(raw_array)
array = []

for i in range(len(raw_array)):
    if abs(raw_array[i]-mean) < mean+10*std:
        array.append(raw_array[i])

# Threshold value (for height of peaks and valleys)
binning = 300
thresh = 20
wdth = 10
prom = 0.1
acc = 1000

counts, bins, bars = plt.hist(array,binning,(np.min(array)*0.5,np.max(array)),alpha=0.75)
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
for i in range(len(peak_idx)-1):
    x_space = np.linspace(x[peak_idx[i]],x[peak_idx[i+1]],acc)
    step = x_space[1]-x_space[0]
    x_gauss = x_space-int(acc/2)*step
    x_gauss = x_gauss[x_gauss >= bins[0]]
    y_gauss = y_intrp(x_gauss)

    try:
        popt, pcov = curve_fit(loggaussian,x_gauss,np.log10(y_gauss),p0=[y[peak_idx[i]],x[peak_idx[i]],5e-7])
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
        initial.append(5e-7)
        print("Peak %i could not be fitted"%i)

try:
    popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
except:
    popt = initial
plt.plot(x[:peak_idx[-1]],gaussian_train(x[:peak_idx[-1]],*popt),label="")

plt.legend()
plt.semilogy()
plt.ylim(thresh*0.9,np.max(counts)*1.1)
plt.xlim(np.min(bins)*0.9,x[peak_idx[-1]]*1.1)
plt.show()