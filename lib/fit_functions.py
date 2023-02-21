import math
import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
from itertools import product

import scipy
from scipy.optimize import curve_fit
from scipy.signal   import find_peaks
from scipy.special import erf
from .io_functions import load_npy, check_key, print_keys
from .ana_functions import generate_cut_array, get_units
np.seterr(divide = 'ignore') 

#===========================================================================#
#********************** TH FUNCTIONS TO USE ********************************#
#===========================================================================#

def gauss(x,a,x0,sigma):
    return a/(sigma*math.sqrt(2*math.pi))*np.exp(-0.5*np.power((x-x0)/sigma,2))

def gaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        center = params[i]
        height = params[i+1]
        width  = params[i+2]
        y      = y + gaussian(x, height, center, width)
    return y

def loggaussian_train(x, *params):
    y = gaussian_train(x, *params)
    return np.log10(y)

def gaussian(x, height, center, width):
    return height * np.exp(-0.5*((x - center)/width)**2)

def pmt_spe(x, height, center, width):
    return height * np.exp(-0.5*((x - center)/width)**2)

def loggaussian(x, height, center, width):
    return np.log10(gaussian(x, height, center, width))

def func(t, t0, sigma, a, tau):
    return (2 * a/tau)*np.exp((sigma/(np.sqrt(2)*tau))**2-(np.array(t)-t0)/tau)*(1-erf((sigma**2-tau*(np.array(t)-t0))/(np.sqrt(2)*sigma*tau)))

def func2(t, p, t0, sigma, a1, tau1, sigma2, a2, tau2):
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma2, a2, tau2)

def logfunc2(t, p, t0, sigma, a1, tau1, a2, tau2):
    return np.log(p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2))

def logfunc3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return np.log(p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3))

def func3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3)

def scfunc(t, a, b, c, d, e, f):
    return (a*np.exp(-(t-c)/b)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(b**2)))*(1-erf(((c-t)/d+d/b)/np.power(2, 0.5))) + (e*np.exp(-(t-c)/f)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(f**2)))*(1-erf(((c-t)/d+d/f)/np.power(2, 0.5)))

#===========================================================================#
#*********************** FITTING FUNCTIONS *********************************#
#===========================================================================#


def gaussian_fit(counts, bins, bars,thresh, fit_function="gaussian", custom_fit=[0]):
    """
    This function fits the histogram, to a gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    """ 
    #### PEAK FINDER PARAMETERS #### thresh = int(len(my_runs[run][ch][key])/1000), wdth = 10 and prom = 0.5 work well
    wdth = 10 # Required width of peaks in samples
    prom = 0.5 # Required prominence of peaks. 
    # The prominence of a peak measures how much a peak stands out from the surrounding baseline of the signal and 
    # is defined as the vertical distance between the peak and its lowest contour line.
    acc  = 1000 # Number of samples to make the initial linear interpolation
    # wlen = # A window length in samples that optionally limits the evaluated area for each peak to a subset of x (Interesting?)

    ## Create linear interpolation between bins to search peaks in these variables ##
    if len(custom_fit) == 2:
        mean  = custom_fit[0]
        sigma = custom_fit[1]

        x = np.linspace(mean-sigma,mean+sigma,acc)
        y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
        y = y_intrp(x)
    else:
        x = np.linspace(bins[1],bins[-2],acc)
        y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
        y = y_intrp(x)

    print("\n...Fitting to a gaussian...")
    ## Find indices of peaks ##
    if fit_function == "gaussian":    peak_idx, _ = find_peaks(y, height = thresh, width = wdth, prominence = prom)
    if fit_function == "loggaussian": peak_idx, _ = find_peaks(np.log10(y), height = np.log10(thresh), width = wdth, prominence = prom)
    
    if len(custom_fit) == 2: 
        print("\n--- Customized fit ---")
        mean  = int(custom_fit[0])
        sigma = int(custom_fit[1])
        best_peak_idx = peak_idx[np.abs(x[peak_idx] - mean ).argmin()]
        best_peak_idx1 = best_peak_idx + 50

        x_gauss = x
        y_gauss = y
        print("Taking peak at: ", x[best_peak_idx])
    else:
        sigma = abs(wdth*(bins[0]-bins[1]))
        best_peak_idx = peak_idx[0]
        best_peak_idx1 = best_peak_idx + 50

        x_space = np.linspace(x[best_peak_idx]-sigma, x[best_peak_idx1]+sigma, acc) #Array with values between the x_coord of 2 consecutives peaks
        step    = x_space[1]-x_space[0]
        x_gauss = x_space-int(acc/2)*step
        x_gauss = x_gauss[x_gauss >= bins[0]]
        y_gauss = y_intrp(x_gauss)
        print("Taking peak at: ", x[best_peak_idx])

    # try:
    popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[best_peak_idx],x[best_peak_idx1],sigma])
    perr = np.sqrt(np.diag(pcov))
    # except:
    #     print("WARNING: Peak could not be fitted")
    
    return x, popt, pcov, perr


def gaussian_train_fit(counts, bins, bars, thresh, fit_function="gaussian"):
    """
    This function fits the histogram, to a train of gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    """ 
    ## Threshold value (for height of peaks and valleys) ##
    # thresh = int(len(my_runs[run][ch][key])/1000)
    wdth   = 10
    prom   = 0.5
    acc    = 1000
    
    ## Create linear interpolation between bins to search peaks in these variables ##
    x = np.linspace(bins[1],bins[-2],acc)
    y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
    y = y_intrp(x)

    ## Find indices of peaks and valleys ##
    if fit_function == "gaussian":
        peak_idx, _ = find_peaks(y, height = thresh, width = wdth, prominence = prom)
        valley_idx, _ = find_peaks(-y, height = [-np.max(counts), -thresh], width = wdth)
    if fit_function == "loggaussian":
        peak_idx, _ = find_peaks(np.log10(y), height = np.log10(thresh), width = wdth, prominence = prom)
        valley_idx, _ = find_peaks(-np.log10(y), height = [-np.max(np.log10(counts)), -np.log10(thresh)], width = wdth, prominence = prom)

    n_peaks = 6
    initial = []                   #Saving for input to the TRAIN FIT
    if len(peak_idx)-1 < n_peaks:
        n_peaks = len(peak_idx)-1  #Number of peaks found by find_peak
    
    for i in range(n_peaks):
        x_space = np.linspace(x[peak_idx[i]], x[peak_idx[i+1]], acc) #Array with values between the x_coord of 2 consecutives peaks
        step    = x_space[1]-x_space[0]
        x_gauss = x_space-int(acc/2)*step
        x_gauss = x_gauss[x_gauss >= bins[0]]
        y_gauss = y_intrp(x_gauss)
        # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.9)

        try:
            # popt, pcov = curve_fit(loggaussian,x_gauss,np.log10(y_gauss),p0=[np.log10(y[peak_idx[i]]),x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
            popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[peak_idx[i]],x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
            perr = np.sqrt(np.diag(pcov))
            ## FITTED to gaussian(x, height, center, width) ##
            initial.append(popt[1])         # HEIGHT
            initial.append(popt[0])         # CENTER
            initial.append(np.abs(popt[2])) # WIDTH
            # plt.plot(x_gauss,gaussian(x_gauss, *popt), ls = "--", c = "black", alpha = 0.5)
        
        except:
            initial.append(x[peak_idx[i]])
            initial.append(y[peak_idx[i]])
            initial.append(abs(wdth*(bins[0]-bins[1])))
            print("Peak %i could not be fitted"%i)

    try:
        ## GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
        if fit_function == "gaussian":    popt, pcov = curve_fit(gaussian_train,x[:peak_idx[-1]], y[:peak_idx[-1]], p0=initial) 
        if fit_function == "loggaussian": popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
        
        perr = np.sqrt(np.diag(pcov))
    except:
        popt = initial
        print("Full fit could not be performed")
    
    return x, y, peak_idx, valley_idx, popt, pcov, perr

def pmt_spe_fit(counts, bins, bars, thresh):
    """
    This function fits the histogram, to a train of gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    [es muy parecida a gaussian_train_fit; hay algunas cosas que las coge en log pero igual se pueden unificar]
    [se le puede dedicar un poco mas de tiempo para tener un ajuste mas fino pero parece que funciona]
    """ 
    ## Threshold value (for height of peaks and valleys) ##
    # thresh = int(len(my_runs[run][ch][key])/1000)
    wdth   = 10
    prom   = 0.5
    acc    = 1000
    
    ## Create linear interpolation between bins to search peaks in these variables ##
    x = np.linspace(bins[1],bins[-2],acc)
    y_intrp = scipy.interpolate.interp1d(bins[:-1],counts)
    y = y_intrp(x)

    ## Find indices of peaks ##
    peak_idx, _ = find_peaks(np.log(y), height = np.log(thresh), width = wdth, prominence = prom)
    # peak_idx, _ = find_peaks(y, height = thresh, width = wdth, prominence = prom)
    ## Find indices of valleys (from inverting the signal) ##
    valley_idx, _ = find_peaks(-np.log(y), height = [-np.max(np.log(counts)), -np.log(thresh)], width = wdth, prominence = prom)
    # valley_idx, _ = find_peaks(-y, height = [-np.max(counts), -thresh], width = wdth)

    n_peaks = 4 #Fit of ped+1pe+2pe
    initial = []                   #Saving for input to the TRAIN FIT
    if len(peak_idx)-1 < n_peaks:
        n_peaks = len(peak_idx)-1  #Number of peaks found by find_peak
    
    for i in range(n_peaks):
        x_space = np.linspace(x[peak_idx[i]], x[peak_idx[i+1]], acc) #Array with values between the x_coord of 2 consecutives peaks
        step    = x_space[1]-x_space[0]
        x_gauss = x_space-int(acc/2)*step
        x_gauss = x_gauss[x_gauss >= bins[0]]
        y_gauss = y_intrp(x_gauss)
        # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.9)

        try:
            popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[peak_idx[i]],x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
            perr = np.sqrt(np.diag(pcov))
            ## FITTED to gaussian(x, height, center, width) ##
            initial.append(popt[1])         # HEIGHT
            initial.append(popt[0])         # CENTER
            initial.append(np.abs(popt[2])) # WIDTH
            # plt.plot(x_gauss,gaussian(x_gauss, *popt), ls = "--", c = "black", alpha = 0.5)
            # plt.ylim((1e-2,1e5))
        except:
            initial.append(x[peak_idx[i]])
            initial.append(y[peak_idx[i]])
            initial.append(abs(wdth*(bins[0]-bins[1])))
            print("Peak %i could not be fitted"%i)

    try:
    # GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
    # popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
        popt, pcov = curve_fit(gaussian_train,x[:peak_idx[-1]], y[:peak_idx[-1]], p0=initial) 
        perr = np.sqrt(np.diag(pcov))
    except:
        popt = initial
        print("Full fit could not be performed")
    
    return x, y, peak_idx, valley_idx, popt, pcov, perr

def peak_fit(fit_raw, raw_x, buffer, thrld, sigma = 1e-8, a_fast = 1e-8, a_slow = 1e-9, OPT={}):

    if check_key(OPT, "CUT_NEGATIVE") == True and OPT["CUT_NEGATIVE"] == True:
        for i in range(len(fit_raw)):
            if fit_raw[i] <= thrld:
                fit_raw[i] = thrld
            if np.isnan(fit_raw[i]):
                fit_raw[i] = thrld

    fit_raw  = fit_raw/np.max(fit_raw)
    t0       = np.argmax(fit_raw) #t0
    raw_x    = np.arange(len(fit_raw))
    guess_t0 = raw_x[np.argmax(fit_raw)-10]
    p = np.mean(fit_raw[:t0-buffer])

    t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
    
    sigma_low = sigma*1e-2;  sigma_high = sigma*1e2
    a1    = a_fast; a1_low = a_fast*1e-2; a1_high = a_fast*1e2                    
    tau1  = 9e-9;   tau1_low = 6e-9;       tau1_high  = 1e-8

    bounds  = ([t0_low, sigma_low, a1_low, tau1_low], [t0_high, sigma_high, a1_high, tau1_high])
    # initial = (t0, sigma, a1, tau1)
    initial  = (t0, 8, 12, 25)
    labels  = ["TIME", "SIGM", "AMP1", "TAU1"]

    # FIT PEAK
    try:
        popt, pcov = curve_fit(func, raw_x[t0-buffer:t0+int(buffer/2)], fit_raw[t0-buffer:t0+int(buffer/2)], p0 = initial, method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except Exception as e:
        if e=='ValueError(\'Residuals are not finite in the initial point.\')':
            pass
        else:
            print("\n --- WARNING: Peak fit could not be performed ---")
            print("ERROR: ", e)
            popt = initial
            perr = np.zeros(len(initial))

    # PRINT FIRST FIT VALUE
    if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
        print("\n--- FIRST FIT VALUES (FAST) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
        print("-------------------------------")

    # EXPORT FIT PARAMETERS
    # a1 = popt[2];sigma = popt[1];tau1 = popt[3];t0 = popt[0]

    return popt, perr

def sipm_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):
    """ DOC """
    max = np.argmax(raw)
    # thrld = 1e-4
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    OPT["CUT_NEGATIVE"] = True
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thrld=thrld, OPT=OPT)

    p  = np.mean(raw[:max-buffer1])
    a1 = 2e-5; a1_low = 1e-8;  a1_high = 9e-2                    
    a2 = 2e-5; a2_low = 1e-8; a2_high = 9e-2                    
    a3 = 2e-5; a3_low = 1e-8; a3_high = 9e-2
    tau1 = 9e-8; tau1_low = 6e-9; tau1_high = 1e-7
    tau2 = 9e-7; tau2_low = tau1_high; tau2_high = 1e-6
    tau3 = 9e-6; tau3_low = tau2_high; tau3_high = 1e-5
    sigma2 = popt1[1]*10; sigma2_low = popt1[1]; sigma2_high = popt1[1]*100

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    bounds2  = ([sigma2_low, a2_low, tau2_low, a3_low, tau3_low], [sigma2_high, a2_high, tau2_high, a3_high, tau3_high])
    initial2 = (sigma2, a2, tau2, a3, tau3)
    labels2  = ["SIGM", "AMP2", "TAU2", "AMP3", "TAU3"]
    popt, pcov = curve_fit(lambda t, sigma2, a2, tau2, a3, tau3: logfunc3(t, p, popt1[0], sigma2, popt1[2], popt1[3], a2, tau2, a3, tau3), raw_x[max-buffer1:max+buffer2], np.log(raw[max-buffer1:max+buffer2]), p0 = initial2, bounds = bounds2, method = "trf")
    perr2 = np.sqrt(np.diag(pcov))

    sigma2 = popt[0];a2 = popt[1];tau2 = popt[2];a3 = popt[3];tau3 = popt[4]
    param  = [p, a1, sigma2, tau1, popt1[3], a2, tau2, a3, tau3]
    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        print("\n--- SECOND FIT VALUES (SLOW) ---")
        for i in range(len(initial2)):
            print("%s: \t%.2E \u00B1 %.2E"%(labels2[i], popt[i], perr2[i]))
        print("--------------------------------\n")

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: 
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1, 2, 1)
        plt.title("First fit to determine peak")
        plt.plot(raw_x, raw, label="raw")
        plt.plot(raw_x[max-buffer1:max+int(buffer1/2)], func(raw_x[max-buffer1:max+int(buffer1/2)], *popt1), label="FIT")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") != False: plt.semilogy();plt.ylim(thrld, raw[max]*1.1)
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.title("Second fit with full wvf")
        plt.plot(raw_x, raw, zorder=0, c="tab:blue", label="raw")
        plt.plot(raw_x[max-buffer1:max+buffer2], func3(raw_x[max-buffer1:max+buffer2], *param), c="tab:orange", label="FIT")
        plt.plot(raw_x, func3(raw_x, *param), c="tab:green", label="FIT_FULL_LENGHT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        if check_key(OPT, "LOGY") != False: plt.semilogy();plt.ylim(thrld, raw[max]*1.1)
        plt.legend()
        
        if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: 
            while not plt.waitforbuttonpress(-1): pass
            plt.clf()

    aux = func3(raw_x, *param)
    return aux,param,perr2

def scint_fit(raw, raw_x, fit_range, thrld=1e-6, sigma = 1e-8, a_fast = 1e-8, a_slow = 1e-9,OPT={}):       
    # Prepare plot vis
    next_plot = False
    plt.rcParams['figure.figsize'] = [8, 8]

    raw     = raw/np.max(raw)
    t0      = np.argmax(raw)
    raw_x   = np.arange(len(raw))
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]
    p       = np.mean(raw[:t0-buffer1])
    OPT["CUT_NEGATIVE"] = True

    # FITTING THE PEAK #
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thrld, sigma, a_fast, a_slow, OPT)
    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    sigm = popt1[1]; sigm_low = sigm*0.9; sigm_high = sigm*1.1
    a1   = popt1[2]; a1_low   = a1*0.9;   a1_high   = a1*1.1  
    tau1 = popt1[3]; tau1_low = tau1*0.9; tau1_high = tau1*1.1  

    a2   = a_slow;   a2_low = a_slow*1e-2; a2_high = a_slow*1e2 #initial input
    tau2 = 1.4e-6; tau2_low = 1.2e-6;    tau2_high = 1.6e-6
    
    # bounds2  = ([sigm_low, a1_low, tau1_low, a2_low, tau2_low], [sigm_high, a1_high, tau1_high, a2_high, tau2_high])
    # initial2 = (sigm, a1, tau1, a2, tau2)
    initial2 = (p, t0, sigm, a1, tau1, 10, 100, 40)
    labels2  = ["p", "t0", "SIGM1", "AMP1", "tau1", "SIGM2", "AMP2", "tau2"]
    
    # Fitting to func2(t, p, t0, sigma, a1, tau1, a2, tau2) =  return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2)
    try:
        popt2, pcov2 = curve_fit(func2,raw_x[buffer1:buffer2], raw[buffer1:buffer2], p0 = initial2, method = "trf")
        perr2 = np.sqrt(np.diag(pcov2))
    except Exception as e:
        if e=='ValueError(\'Residuals are not finite in the initial point.\')':
            pass
        else:
            print("\n --- WARNING: Fit could not be performed ---")
            print("ERROR: ", e)
            popt2 = initial2
            perr2 = np.zeros(len(popt2))

    t0     = popt1[0]
    sigma1 = popt1[2]; a1 = popt2[3] ; tau1 = popt2[4]
    sigma2 = popt2[5]; a2 = popt2[6] ; tau2 = popt2[7]
    
    param = [p, t0, sigma1, a1, tau1, sigma2, a2, tau2]
    
    if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
        if check_key(OPT, "COLOR") == True: color = OPT["COLOR"]
        else: color = "tab:red"
        print("\n--- SECOND FIT VALUES (SLOW) ---")
        for i in range(len(initial2)):
            print("%s:\t%.2E\t%.2E"%(labels2[i], popt2[i], perr2[i]))
        print("--------------------------------\n")

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:    
        # print("SHOW key not included in OPT")
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1, 2, 1)
        plt.title("First fit to determine peak")
        # plt.plot(raw_x, raw, label="raw", c=color)
        plt.plot(raw_x, raw, label="raw")
        # plt.plot(raw_x[t0-buffer1:t0+int(buffer1/2)], func(raw_x[t0-buffer1:t0+int(buffer1/2)], *popt1), label="FIT")
        plt.plot(raw_x[buffer1:buffer2], func(raw_x[buffer1:buffer2], *popt1), label="FIT")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy();plt.ylim(thrld, raw[np.argmax(raw)]*2)
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.title("Second fit with full wvf")
        # plt.plot(raw_x, raw, zorder=0, label="raw", c=color)
        plt.plot(raw_x, raw, zorder=0, label="raw")
        # plt.plot(raw_x[t0-buffer1:t0+buffer2], func2(raw_x[t0-buffer1:t0+buffer2], *param), label="FIT")
        plt.plot(raw_x[buffer1:buffer2], func2(raw_x[buffer1:buffer2], *param),label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        # plt.axvline(raw_x[t0+buffer2], ls = "--", c = "k")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy(); plt.ylim(thrld, raw[np.argmax(raw)]*2)
        plt.legend()

        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    
    aux = func2(raw_x, *param)
    return aux, param, perr2

def sc_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):
    # Prepare plot vis
    next_plot = False
    plt.rcParams['figure.figsize'] = [8, 8]
    
    t0       = np.argmax(raw)
    raw_x    = np.arange(len(raw))
    initial  = (1500, 150, t0, 8, -700, 300)
    # bounds = ([-200, 10, t0*0.1, 1, -1500, 10], [10000, 3000, t0*10, 20, 1500, 1000])
    labels   = ["AMP", "tau1", "T0", "sigma", "AMP2", "tau2"]

    try:
        popt, pcov = curve_fit(scfunc, raw_x[fit_range[0]:fit_range[1]], raw[fit_range[0]:fit_range[1]], p0 = initial, method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except:
        print("Fit did not succeed")
        popt = initial
        perr = np.zeros(len(initial))

    if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
        print("\n--- FIT VALUES (SLOW) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
        print("--------------------------------\n")

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        plt.title("Fit with full wvf")
        plt.plot(raw_x, raw, zorder=0, c="tab:blue", label="raw")
        plt.plot(raw_x, scfunc(raw_x, *popt), "tab:orange", label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: 
            plt.semilogy()
            plt.ylim(thrld, raw[t0]*1.1)
        plt.legend()
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    
    aux = scfunc(raw_x, *popt)
    # print("\n")
    return aux,popt,perr

def fit_wvfs(my_runs, signal_type, thrld, fit_range=[0,0], sigma = 1e-8, a_fast = 1e-8, a_slow = 1e-9, in_key=["ADC"], out_key="", OPT={}):
    """ DOC """

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ion()
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], in_key):
        aux = dict()
        if key.startswith("Dec"): OPT["COLOR"] = "tab:red"
        raw = my_runs[run][ch][key]        
        raw_x = my_runs[run][ch]["Sampling"]*np.arange(len(raw[0]))
        for i in range(len(raw)):
            print("Fitting wvf ", i)
            if check_key(OPT, "NORM") == True and OPT["NORM"] == True: raw[i] = raw[i]/np.max(raw[i])
            raw[i] = raw[i]/np.max(raw[i])
            if signal_type == "SiPM":  fit, popt, perr = sipm_fit(raw[i], raw_x, fit_range, thrld, OPT)
            if signal_type == "SC":    fit, popt, perr = sc_fit(raw[i],   raw_x, fit_range, thrld, OPT)
            if signal_type == "Scint": fit, popt, perr = scint_fit(raw[i],raw_x, fit_range, thrld, sigma, a_fast, a_slow, OPT)
            aux[i] = fit
         
        my_runs[run][ch]["Fit"+signal_type+out_key] = aux

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ioff()
    print("\n")

# Scintillation profile
    # print("VALUES OF THE FIT: ")
    # print("PED +- DPED:",  ['{:.2E}'.format(item) for item in [popt[0], perr[0]]])
    # print("t0 +- Dt0:",    ['{:.2f}'.format(item) for item in [popt[1], perr[1]]])
    # print("SIG1 +- DSIG1:",['{:.2f}'.format(item) for item in [popt[2], perr[2]]])
    # print("AMP1 +- DAMP1", ['{:.2f}'.format(item) for item in [popt[3], perr[3]]])
    # print("TAU1 +- DTAU1", ['{:.2f}'.format(item) for item in [popt[4], perr[4]]])
    # print("SIG2 +- DSIG2", ['{:.2f}'.format(item) for item in [popt[5], perr[5]]])
    # print("AMP2 +- DAMP2", ['{:.2f}'.format(item) for item in [popt[6], perr[6]]])
    # print("TAU2 +- DTAU2", ['{:.2f}'.format(item) for item in [popt[7], perr[7]]])

    return fit, popt