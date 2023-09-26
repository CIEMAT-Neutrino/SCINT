#================================================================================================================================================#
# This library contains functions to perform fits to the data.                                                                                   #
#================================================================================================================================================#

import os, stat, math, scipy
import numpy             as np
import matplotlib.pyplot as plt
from itertools      import product
from scipy.optimize import curve_fit
from scipy.signal   import find_peaks
from scipy.special  import erf
from scipy.stats    import poisson

np.seterr(divide = 'ignore') 

# THIS LIBRARY NEED MIMO PORQUE HAY COSAS REDUNDAANTES QUE SE PUEDEN UNIFICAR

def fit_gaussians(x, y, *p0):
    assert x.shape == y.shape, "Input arrays must have the same shape."
    popt, pcov = curve_fit(gaussian_train, x,y, p0=p0[0])
    fit_y=gaussian_train(x,*popt)
    chi_squared = np.sum((y[abs(fit_y)>0.1] - fit_y[abs(fit_y)>0.1]) ** 2 / fit_y[abs(fit_y)>0.1]) / (y.size - len(popt))
    return popt,fit_y, chi_squared

##Binomial+Poisson distribution
from math import factorial as fact
import numpy as np
from scipy.stats import poisson
def B(i,k,debug=False):
    '''
    Factorial factor of F
    '''
    if (i==0) & (k==0):return 1;
    if (i==0) & (k>0): return 0;
    else:              return ( fact(k-1)*fact(k) / (fact(i-1)*fact(i)*fact(k-i)) )

def F(K,p,L,debug=False):
    '''
    Computes prob of the kth point in a convoluted poisson+binomial distribution,.
    L is the mean value of the poisson, p is the binomial coef, i.e. the crosstalk we want to compute
    '''

    aux_sum=0
    if debug: print(K)
    for i in range(K+1): aux_sum+=B(i,K)*((L *(1 - p))**i)  *  (p**(K - i)) 
    return np.exp(-L)*aux_sum/fact(K);

def PoissonPlusBinomial(x,p,L,debug=False):
    N   = len(x)
    aux = np.zeros(shape=N)
    for i in range(N):
        if debug: print(x,i,x[i])
        aux[i] = F(int(x[i]),p,L);
    return aux/sum(aux);

#===========================================================================#
#********************** TH FUNCTIONS TO USE ********************************#
#===========================================================================#
def chi_squared(x,y,popt):
    fit_y = np.sum([gaussian(x, popt[j], popt[j+1], popt[j+2]) for j in range(0, len(popt), 3)])
    return np.sum((y - fit_y) ** 2 / fit_y) / (y.size - len(popt))

def pure_scint(time,t0,a1,a2,tau1,tau2):
    y = a1*np.exp(-(time-t0)/tau1)+a2*np.exp(-(time-t0)/tau2)

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

def logfunc2(t, p, t0, sigma1, a1, tau1, sigma2, a2, tau2):
    return np.log(p + func(t, t0, sigma1, a1, tau1) + func(t, t0, sigma2, a2, tau2))

def logfunc3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return np.log(p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3))

def func3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3)

def scfunc(t, a, b, c, d, e, f):
    return (a*np.exp(-(t-c)/b)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(b**2)))*(1-erf(((c-t)/d+d/b)/np.power(2, 0.5))) + (e*np.exp(-(t-c)/f)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(f**2)))*(1-erf(((c-t)/d+d/f)/np.power(2, 0.5)))

def dec_gauss(f, fc, n):
    y = np.exp(-0.5*(f/fc)**n)
    return y

def fit_dec_gauss(f, fc, n):
    y = np.log10(dec_gauss(f, fc, n)); y[0] = 0
    return y

#===========================================================================#
#*********************** FITTING FUNCTIONS *********************************#
#===========================================================================#


def gaussian_fit(counts, bins, bars, thresh, fit_function="gaussian", custom_fit=[0]):
    '''
    This function fits the histogram, to a gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    ''' 

    #### PEAK FINDER PARAMETERS #### thresh = int(len(my_runs[run][ch][key])/1000), wdth = 10 and prom = 0.5 work well
    wdth = 10
    prom = 0.5
    acc  = 1000

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
        mean  = float(custom_fit[0])
        sigma = float(custom_fit[1])
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
    popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[best_peak_idx],x[best_peak_idx1],sigma],maxfev=5000)
    # popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[best_peak_idx],x[best_peak_idx1]],sigma = sigma, absolute_sigma=True, maxfev=5000)
    perr = np.sqrt(np.diag(pcov))
    chi2 = chi_squared(x_gauss,y_gauss,popt)
    # except:
    #     print("WARNING: Peak could not be fitted")
    
    return x, popt, pcov, perr
    # return x, popt, pcov, perr, chi2 # UPLOAD WHEN POSSIBLE MERGING IN MAIN BRANCH; upgrade all the fit functions


def gaussian_train_fit(counts, bins, bars, params, debug=False):
    ''' 
    This function fits the histogram, to a train of gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    ''' 

    #Imports from other libraries
    from .io_functions import print_colored

    ## Threshold value (for height of peaks and valleys) ##
    # thresh = int(len(my_runs[run][ch][key])/1000)
    thresh       = params["THRESHOLD"]
    wdth         = params["WIDTH"]
    prom         = params["PROMINENCE"]
    acc          = params["ACCURACY"]
    fit_function = params["FIT"]
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
    if len(peak_idx) < n_peaks:
        n_peaks = len(peak_idx)  #Number of peaks found by find_peak
    
    for i in range(n_peaks):
        try:
            x_space = np.linspace(x[peak_idx[i]], x[peak_idx[i+1]], acc) #Array with values between the x_coord of 2 consecutives peaks
            step = x_space[1]-x_space[0]
            x_gauss = x_space-int(acc/2)*step
        except IndexError:
            x_space = np.linspace(x[peak_idx[i-1]], x[i], acc)
            step = x_space[1]-x_space[0]
            x_gauss = x_space+int(acc/2)*step

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
            print_colored("Peak %i could not be fitted"%i, "ERROR")

    try:
        ## GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
        if fit_function == "gaussian":    popt, pcov = curve_fit(gaussian_train,x, y, p0=initial) 
        if fit_function == "loggaussian": popt, pcov = curve_fit(loggaussian_train,x,np.log10(y),p0=initial)
        
        perr = np.sqrt(np.diag(pcov))
    except:
        popt = initial
        print_colored("Full fit could not be performed", "ERROR")
    
    return x, y, peak_idx, valley_idx, popt, pcov, perr

def pmt_spe_fit(counts, bins, bars, thresh):
    '''
    This function fits the histogram, to a train of gaussians, which has been previoulsy visualized with: 
    **counts, bins, bars = vis_var_hist(my_runs, run, ch, key, OPT=OPT)**
    And return the parameters of the fit (if performed)
    [es muy parecida a gaussian_train_fit; hay algunas cosas que las coge en log pero igual se pueden unificar]
    [se le puede dedicar un poco mas de tiempo para tener un ajuste mas fino pero parece que funciona]
    ''' 

    #Imports from other libraries
    from .io_functions import print_colored

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
            print_colored("Peak %i could not be fitted"%i, "ERROR")

    try:
    # GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
    # popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
        popt, pcov = curve_fit(gaussian_train,x[:peak_idx[-1]], y[:peak_idx[-1]], p0=initial) 
        perr = np.sqrt(np.diag(pcov))
    except:
        popt = initial
        print_colored("Full fit could not be performed", "ERROR")
    
    return x, y, peak_idx, valley_idx, popt, pcov, perr

def peak_fit(fit_raw, raw_x, buffer, thrld, sigma_fast = 1e-9, a_fast = 1, tau_fast = 1e-8, OPT={}):
    ''' 
    This function fits the peak to a gaussian function, and returns the parameters
    '''

    # Imports from other libraries
    from .io_functions import check_key

    raw_max = np.argmax(fit_raw)

    if check_key(OPT, "CUT_NEGATIVE") == True and OPT["CUT_NEGATIVE"] == True:
        for i in range(len(fit_raw)):
            if fit_raw[i] <= thrld:  fit_raw[i] = thrld
            if np.isnan(fit_raw[i]): fit_raw[i] = thrld

    guess_t0 = raw_x[raw_max]
    p = np.mean(fit_raw[:raw_max-buffer])

    t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
    
    sigma = sigma_fast;   sigma_low = sigma*1e-2;  sigma_high = sigma*1e2
    a1    = a_fast;       a1_low    = a_fast*1e-2; a1_high    = a_fast*1e2                    
    tau1  = tau_fast;     tau1_low  = 6e-9;        tau1_high  = tau1*1e2

    bounds  = ([t0_low, sigma_low, a1_low, tau1_low], [t0_high, sigma_high, a1_high, tau1_high])
    initial = [t0, sigma, a1, tau1]
    labels  = ["TIME", "SIGM", "AMP1", "TAU1"]

    # FIT PEAK
    # try:
    popt, pcov = curve_fit(func, raw_x[raw_max-buffer:raw_max+int(buffer/2)], fit_raw[raw_max-buffer:raw_max+int(buffer/2)], p0 = initial)
    perr = np.sqrt(np.diag(pcov))
    # except:
        #print("Peak fit could not be performed")
        #popt = initial
        #perr = np.zeros(len(initial))

    # PRINT FIRST FIT VALUE
    if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
        print("\n--- FISRT FIT VALUES (FAST) ---")
        for i in range(len(initial)): print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
        print("-------------------------------")

    # EXPORT FIT PARAMETERS
    # a1 = popt[2];sigma = popt[1];tau1 = popt[3];t0 = popt[0]

    return popt, perr

def sipm_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):
    ''' 
    DOC 
    '''

    # Imports from other libraries
    from .io_functions import check_key


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

    return aux,param,perr2,labels2

def scint_fit(raw, raw_x, fit_range, thrld=1e-6, i_param={}, OPT={}):
    ''' 
    DOC 
    '''

    # Imports from other libraries
    from .io_functions import check_key, print_colored

    next_plot = False
    OPT["CUT_NEGATIVE"] = True
    
    # Define input parameters from dictionary
    sigma    = i_param["sigma"]
    a_fast   = i_param["a_fast"]
    tau_fast = i_param["tau_fast"]
    a_slow   = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]
    
    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]; buffer2 = fit_range[1]
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thrld, sigma, a_fast, tau_fast, OPT)
    
    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    p = np.mean(raw[:raw_max-buffer1]); p_std = np.std(raw[:raw_max-buffer1]);
    
    sigma1 = popt1[1]; sigma1_low = sigma1*0.9;    sigma1_high = sigma1*1.1
    a1     = popt1[2]; a1_low     = a1*0.9;        a1_high     = a1*1.1
    tau1   = popt1[3]; tau1_low   = tau1*0.9;      tau1_high   = tau1*1.1
    
    sigma2 = sigma;    sigma2_low = sigma*0.9;     sigma2_high = sigma*1.1
    a2     = a_slow;   a2_low     = a_slow*1e-2;   a2_high     = a_slow*1e2
    tau2   = tau_slow; tau2_low   = tau_slow*1e-2; tau2_high   = tau_slow*1e2
    
    bounds2  = ([a1_low, sigma2_low, a2_low, tau2_low], [a1_high, sigma2_high, a2_high, tau2_high])
    initial2 = (a1, sigma2, a2, tau2)
    labels2  = ["AMP1", "SIG2", "AMP2", "TAU2"]
    
    try:
        popt2, pcov2 = curve_fit(lambda t, a1, sigma2, a2, tau2: logfunc2(t, p, popt1[0], popt1[1], a1, popt1[3], sigma2, a2, tau2), raw_x[raw_max-buffer1:raw_max+buffer2], np.log(raw[raw_max-buffer1:raw_max+buffer2]), p0 = initial2)
        perr2 = np.sqrt(np.diag(pcov2))
    
    except:
        print_colored("Fit could not be performed", "ERROR")
        popt2 = initial2
        perr2 = np.zeros(len(popt2))
    
    t0    = popt1[0]; a1 = popt2[0]
    sigma2 = popt2[1]; a2 = popt2[2] ; tau2 = popt2[3]
    
    labels = ["PED", "T0",     "SIG1",   "AMP1",   "TAU1",   "SIG2",   "AMP2",   "TAU2"  ]
    param  = [p,     popt1[0], popt1[1], popt2[0], popt1[2], popt2[1], popt2[2], popt2[3]]
    perr   = [p_std, perr1[0], perr1[1], perr2[0], perr1[2], perr2[1], perr2[2], perr2[3]] 
    
    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        # print("SHOW key not included in OPT")
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1, 2, 1)
        plt.title("First fit to determine peak")
        plt.plot(raw_x, raw, label="raw", c=color)
        plt.plot(raw_x[max-buffer1:max+int(buffer1/2)], func(raw_x[max-buffer1:max+int(buffer1/2)], *popt1), label="FIT")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy();plt.ylim(thrld, raw[max]*1.1)
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.title("Second fit with full wvf")
        plt.plot(raw_x, raw, zorder=0, label="raw", c=color)
        plt.plot(raw_x[max-buffer1:max+buffer2], func2(raw_x[max-buffer1:max+buffer2], *param), label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        plt.axvline(raw_x[max+buffer2], ls = "--", c = "k")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy();plt.ylim(thrld, raw[max]*1.1)
        plt.legend()
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    
    aux = func2(raw_x, *param)
    return aux,param,perr,labels

def sc_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):

    # Imports from other libraries
    from .io_functions import check_key, print_colored

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
        print_colored("Fit did not succeed", "ERROR")
        popt = initial
        perr = np.zeros(len(initial))

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
    return aux,popt,perr,labels

def fit_wvfs(my_runs,signal_type,thrld,fit_range=[0,200],i_param={},in_key=["ADC"],out_key="",OPT={}):
    ''' 
    DOC 
    '''

    # Imports from other libraries
    from .io_functions  import check_key
    from .ana_functions import find_amp_decrease

    i_param = get_initial_parameters(i_param)

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ion()
    
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], in_key):
        aux = dict()
        raw = my_runs[run][ch][key]
        raw_x = my_runs[run][ch]["Sampling"]*np.arange(len(raw[0]))
        
        for i in range(len(raw)):
            raw_max = np.max(raw[i])
            raw[i] = raw[i]/raw_max
            if signal_type == "SiPM":  fit, popt, perr, labels = sipm_fit(raw[i], raw_x, fit_range, thrld, OPT)
            if signal_type == "SC":    fit, popt, perr, labels = sc_fit(raw[i],   raw_x, fit_range, thrld, OPT)
            if signal_type == "Scint": fit, popt, perr, labels = scint_fit(raw[i],raw_x, fit_range, thrld, i_param, OPT)
            if signal_type == "SimpleScint": fit, popt, perr, labels = simple_scint_fit(raw[i],raw_x, fit_range, i_param, OPT)
            if signal_type == "TauSlow": fit, popt, perr, labels = tau_fit(raw[i],raw_x, fit_range, i_param, OPT)
            aux[i] = fit*raw_max
            raw[i] = raw[i]*raw_max
            i_idx, f_idx = find_amp_decrease(aux[i],1e-3)
            PE = np.sum(raw[i])
            PE_std = np.std(raw[i][:i_idx])
            
            if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
                print("Fitting wvf %i for run %i, ch %i"%(i,run,ch))
                
                print("\n---------- TOTAL FIT ----------")
                with open("../fit_data/DeconvolutionFit_%i_%i.txt"%(run,ch),"w+") as f:
                    f.write("%s:\t%.2f\t%.2f\n"%("PE", PE, PE_std))
                    for i in range(len(labels)):
                        print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
                        f.write("%s:\t%.4E\t%.4E\n"%(labels[i], popt[i], perr[i]))
                f.close()
                os.chmod("../fit_data/DeconvolutionFit_%i_%i.txt"%(run,ch), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                print("--------------------------------\n")
        
        my_runs[run][ch]["Fit"+signal_type+out_key] = aux

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ioff()
    print("\n")

    return fit, popt

def get_initial_parameters(i_param):
    '''
    DOC
    '''
    # Imports from other libraries
    from .io_functions import check_key
    
    # Define input parameters from dictionary
    if check_key(i_param,"ped")      == False: i_param["ped"]      = 1e-6
    if check_key(i_param,"t0")       == False: i_param["t0"]       = 1e-6
    if check_key(i_param,"sigma")    == False: i_param["sigma"]    = 1e-8
    if check_key(i_param,"const")    == False: i_param["const"]    = 1e-8
    if check_key(i_param,"a_fast")   == False: i_param["a_fast"]   = 1e-2
    if check_key(i_param,"tau_fast") == False: i_param["tau_fast"] = 1e-8
    if check_key(i_param,"a_slow")   == False: i_param["a_slow"]   = 1e-2
    if check_key(i_param,"tau_slow") == False: i_param["tau_slow"] = 1e-6
    
    return i_param

def scint_profile(x,const,a_f,tau_f,tau_s):
    return const*(2*a_f/tau_f*np.exp(-(x)/tau_f) + 2*(1-a_f)/tau_s*np.exp(-(x)/tau_s))

def log_scint_profile(x,const,a_f,tau_f,tau_s):
    return np.log(scint_profile(x,const,a_f,tau_f,tau_s))

def tau_slow_profile(x,a_s,tau_s):
    return 2*a_s/tau_s*np.exp(-(x)/tau_s)

def log_tau_slow_profile(x,a_s,tau_s):
    return np.log(tau_slow_profile(x,a_s,tau_s))

def simple_scint_fit(raw, raw_x, fit_range, i_param={}, OPT={}):
    """ DOC """

    # Imports from other libraries
    from .io_functions import check_key

    next_plot = False
    thrld = 1e-10
    for i in range(len(raw)):
        if raw[i] <= thrld:
            raw[i] = thrld
        if np.isnan(raw[i]):
            raw[i] = thrld
    # Define input parameters from dictionary
    const    = i_param["const"]
    a_fast   = i_param["a_fast"]
    tau_fast = i_param["tau_fast"]
    a_slow   = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]
    
    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]; buffer2 = fit_range[1]
    
    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    a1     = a_fast; a1_low     = a1*0.9;        a1_high     = a1*1.1
    tau1   = tau_fast; tau1_low   = tau1*0.9;      tau1_high   = tau1*1.1
    
    a2     = a_slow;   a2_low     = a_slow*1e-2;   a2_high     = a_slow*1e2
    tau2   = tau_slow; tau2_low   = tau_slow*1e-2; tau2_high   = tau_slow*1e2
    
    const_high = const*100; const_low = const*0.01

    bounds2  = ([const_low, a1_low, tau1_low, tau2_low], [const_high, a1_high, tau1_high, tau2_high])
    initial2 = (const, a1, tau1, tau2)
    labels2  = ["CONST", "AMP1", "TAU1", "TAU2"]
    
    # try:
    # popt, pcov = curve_fit(scint_profile, raw_x[:buffer2] ,raw[raw_max:raw_max+buffer2],p0=initial2, bounds=bounds2)
    popt, pcov = curve_fit(log_scint_profile, raw_x[:buffer2] ,np.log(raw[raw_max:raw_max+buffer2]),p0=initial2, bounds=bounds2)
    perr = np.sqrt(np.diag(pcov))
    
    # except:
    # print("Fit could not be performed")
    # popt2 = initial2
    # perr2 = np.zeros(len(popt2))
    zeros_aux = np.zeros(raw_max)
    zeros_aux2 = np.zeros(len(raw)- raw_max-buffer2 )
    
    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        # print("SHOW key not included in OPT")
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1, 1, 1)
        plt.title("First fit to determine peak")
        plt.plot(raw_x, raw, label="raw", c="black")
        plt.plot(raw_x, np.concatenate([zeros_aux, scint_profile(raw_x[:-raw_max], *popt)]), label="FIT")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy()
        plt.legend()
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()

    aux = np.concatenate([zeros_aux, scint_profile(raw_x[:buffer2], *popt), zeros_aux2])
    return aux,popt,perr,labels2

def tau_fit(raw, raw_x, fit_range, i_param={}, OPT={}):
    """ DOC """

    # Imports from other libraries
    from .io_functions import check_key
    
    next_plot = False
    # thrld = 1e-10
    # for i in range(len(raw)):
    #     if raw[i] <= thrld:
    #         raw[i] = thrld
    #     if np.isnan(raw[i]):
    #         raw[i] = thrld
    # Define input parameters from dictionary
    a_slow   = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]
    
    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]; buffer2 = fit_range[1]
    
    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    a2     = a_slow;   a2_low     = a_slow*1e-2;   a2_high     = a_slow*1e2
    tau2   = tau_slow; tau2_low   = tau_slow*1e-2; tau2_high   = tau_slow*1e2
    

    bounds2  = ([a2_low, tau2_low], [a2_high, tau2_high])
    labels2  = ["AMP2","TAU2"]
    initial2 = (a2, tau2)
    # try:
    # popt, pcov = curve_fit(scint_profile, raw_x[:buffer2] ,raw[raw_max:raw_max+buffer2],p0=initial2, bounds=bounds2)
    popt, pcov = curve_fit(log_tau_slow_profile, raw_x[:buffer2-buffer1] ,np.log(raw[raw_max+buffer1:raw_max+buffer2]),p0=initial2, bounds=bounds2)
    perr = np.sqrt(np.diag(pcov))
    
    # except:
    # print("Fit could not be performed")
    # popt2 = initial2
    # perr2 = np.zeros(len(popt2))
    zeros_aux = np.zeros(raw_max+buffer1)
    zeros_aux2 = np.zeros(len(raw) - raw_max - buffer2)
    
    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        # print("SHOW key not included in OPT")
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1, 1, 1)
        plt.title("First fit to determine peak")
        plt.plot(raw_x, raw, label="raw", c="black")
        plt.plot(raw_x, np.concatenate([zeros_aux, tau_slow_profile(raw_x[:buffer2-buffer1], *popt), zeros_aux2]), label="FIT")
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: plt.semilogy()
        plt.legend()
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()

    aux = np.concatenate([zeros_aux, tau_slow_profile(raw_x[:buffer2-buffer1], *popt), zeros_aux2])
    return aux,popt,perr,labels2
