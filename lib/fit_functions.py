import numpy as np
import scipy as sc
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.special import erf

from .io_functions import load_npy, check_key

from itertools import product

def gaussian_train(x, *params):
    """ DOC """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y   = y + amp * np.exp( -((x - ctr)/wid)**2)
    return y

def loggaussian_train(x, *params):
    """ DOC """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y   = y + amp * np.exp( -((x - ctr)/wid)**2)
    return np.log10(y)

def gaussian(x, height, center, width):
    """ DOC """
    return height * np.exp(-(x - center)**2/(2 * width**2))

def loggaussian(x, height, center, width):
    """ DOC """
    return np.log10(gaussian(x, height, center, width))

def func(t, t0, sigma, a, tau):
    """ DOC """
    return (2 * a/tau)*np.exp((sigma/(np.sqrt(2)*tau))**2-(np.array(t)-t0)/tau)*(1-erf((sigma**2-tau*(np.array(t)-t0))/(np.sqrt(2)*sigma*tau)))

def func2(t, p, t0, sigma, a1, tau1, a2, tau2):
    """ DOC """
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2)

def logfunc2(t, p, t0, sigma, a1, tau1, a2, tau2):
    """ DOC """
    return np.log(p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2))

def logfunc3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    """ DOC """
    return np.log(p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3))

def func3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    """ DOC """
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma, a2, tau2) + func(t, t0, sigma, a3, tau3)

def scfunc(t, a, b, c, d, e, f):
    """ DOC """
    return (a*np.exp(-(t-c)/b)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(b**2)))*(1-erf(((c-t)/d+d/b)/np.power(2, 0.5)))+(e*np.exp(-(t-c)/f)/np.power(2*np.pi, 0.5)*np.exp(-d**2/(f**2)))*(1-erf(((c-t)/d+d/f)/np.power(2, 0.5)))

def sipm_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):
    """ DOC """
    max = np.argmax(raw)
    # thrld = 1e-4
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    OPT["CUT_NEGATIVE"] = True
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, OPT)

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

    while not plt.waitforbuttonpress(-1): pass
    plt.clf()
    aux = func3(raw_x, *param)
    plt.ioff()
    return aux,param

def scint_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):       
    """ DOC """

    next_plot = False
    max = np.argmax(raw)
    # thrld = 1e-10
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    OPT["CUT_NEGATIVE"] = True
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thrld, OPT)

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    p = np.mean(raw[:max-buffer1])

    sigm = popt1[1]; sigm_low = sigm*0.9; sigm_high = sigm*1.1
    a1   = popt1[2]; a1_low   = a1*0.9;   a1_high   = a1*1.1  
    tau1 = popt1[3]; tau1_low = tau1*0.9; tau1_high = tau1*1.1  

    a2   = 2e-8;   a2_low = 6e-9;   a2_high = 9e-4
    tau2 = 8e-7; tau2_low = 5e-7; tau2_high = 1e-6
    
    bounds2  = ([sigm_low, a1_low, tau1_low, a2_low, tau2_low], [sigm_high, a1_high, tau1_high, a2_high, tau2_high])
    initial2 = (sigm, a1, tau1, a2, tau2)
    labels2  = ["SIGM", "AMP1", "tau1", "AMP2", "tau2"]

    try:
        popt2, pcov2 = curve_fit(lambda t, sigma, a1, tau1, a2, tau2: logfunc2(t, p, popt1[0], sigma, a1, tau1, a2, tau2), raw_x[max-buffer1:max+buffer2], np.log(raw[max-buffer1:max+buffer2]), p0 = initial2, bounds = bounds2, method = "trf")
        # popt2, pcov2 = curve_fit(lambda t, sigma, a1, tau1, a2, tau2: func2(t, p, popt1[0], sigma, a1, tau1, a2, tau2), raw_x[max-buffer1:max+buffer2], np.log(raw[max-buffer1:max+buffer2]), p0 = initial2, bounds = bounds2, method = "trf")
        perr2 = np.sqrt(np.diag(pcov2))
    except:
        print("Fit could not be performed")
        popt2 = initial2
        perr2 = np.zeros(len(popt2))

    t0    = popt1[0]; a1 = popt2[1] ; tau1 = popt2[2]
    sigma = popt2[0]; a2 = popt2[3] ; tau2 = popt2[4]
    
    param = [p, t0, sigma, a1, tau1, a2, tau2]
    
    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        if check_key(OPT, "COLOR") == True: color = OPT["COLOR"]
        else: color = "tab:red"
        print("\n--- SECOND FIT VALUES (SLOW) ---")
        for i in range(len(initial2)):
            print("%s:\t%.2E\t%.2E"%(labels2[i], popt2[i], perr2[i]))
        print("--------------------------------\n")

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
    return aux,param

def sc_fit(raw, raw_x, fit_range, thrld=1e-6, OPT={}):
    """ DOC """
    # Prepare plot vis
    next_plot = False
    plt.rcParams['figure.figsize'] = [8, 8]
    
    raw_x = np.arange(len(raw))

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    t0 = np.argmax(raw)
    
    initial = (1500, 150, t0, 8, -700, 300)
    # bounds = ([-200, 10, t0*0.1, 1, -1500, 10], [10000, 3000, t0*10, 20, 1500, 1000])
    labels = ["AMP", "tau1", "T0", "sigma", "AMP2", "tau2"]

    try:
        popt, pcov = curve_fit(scfunc, raw_x[fit_range[0]:fit_range[1]], raw[fit_range[0]:fit_range[1]], p0 = initial, method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except:
        print("Fit did not succeed")
        popt = initial
        perr = np.zeros(len(initial))

    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        print("\n--- FIT VALUES (SLOW) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
        print("--------------------------------\n")

        plt.title("Fit with full wvf")
        plt.plot(raw_x, raw, zorder=0, c="tab:blue", label="raw")
        plt.plot(raw_x, scfunc(raw_x, *popt), "tab:orange", label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True: 
            plt.semilogy()
            plt.ylim(thrld, raw[t0]*1.1)
        plt.legend()

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: 
        while not plt.waitforbuttonpress(-1): pass
        plt.clf()
    
    aux = scfunc(raw_x, *popt)
    # print("\n")
    return aux,popt

def peak_fit(fit_raw, raw_x, buffer, thrld, OPT):
    """ DOC """

    max = np.argmax(fit_raw)
    # print(fit_raw)
    if check_key(OPT, "CUT_NEGATIVE") == True and OPT["CUT_NEGATIVE"] == True:
        for i in range(len(fit_raw)):
            if fit_raw[i] <= thrld:
                fit_raw[i] = thrld
            if np.isnan(fit_raw[i]):
                fit_raw[i] = thrld

    guess_t0 = raw_x[np.argmax(fit_raw)-10]
    p = np.mean(fit_raw[:max-buffer])

    t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
    
    sigma = 1e-8; sigma_low = 6e-9; sigma_high = 9e-6
    a1    = 5e-8;    a1_low = 1e-9;    a1_high = 9e-6                    
    tau1  = 1e-8;  tau1_low = 6e-9;  tau1_high = 1e-6

    bounds  = ([t0_low, sigma_low, a1_low, tau1_low], [t0_high, sigma_high, a1_high, tau1_high])
    initial = (t0, sigma, a1, tau1)
    labels  = ["TIME", "SIGM", "AMP1", "TAU1"]

    # FIT PEAK
    try:
        popt, pcov = curve_fit(func, raw_x[max-buffer:max+int(buffer/2)], fit_raw[max-buffer:max+int(buffer/2)], p0 = initial, bounds = bounds, method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except:
        print("Peak fit could not be performed")
        popt = initial
        perr = np.zeros(len(initial))

    # PRINT FIRST FIT VALUE
    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        print("\n--- FISRT FIT VALUES (FAST) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i], popt[i], perr[i]))
        print("-------------------------------")

    # EXPORT FIT PARAMETERS
    # a1 = popt[2];sigma = popt[1];tau1 = popt[3];t0 = popt[0]

    return popt, perr

def fit_wvfs(my_runs, signal_type, thrld, fit_range=[0,0], KEYS=["ADC"], OPT={}):
    """ DOC """

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ion()
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], KEYS):
        aux = dict()
        if key.startswith("Dec"): OPT["COLOR"] = "tab:red"
        raw = my_runs[run][ch][key]        
        raw_x = my_runs[run][ch]["Sampling"]*np.arange(len(raw[0]))
        # print(raw)
        for i in range(len(raw)):
            print("Fitting wvf ", i)
            # print(raw[i])
            if check_key(OPT, "NORM") == True and OPT["NORM"] == True: raw[i] = raw[i]/np.max(raw[i])
            if signal_type == "SiPM":  fit,popt = sipm_fit(raw[i], raw_x, fit_range, thrld, OPT)
            if signal_type == "Scint": fit,popt = scint_fit(raw[i], raw_x, fit_range, thrld, OPT)
            if signal_type == "SC":    fit,popt = sc_fit(raw[i], raw_x, fit_range, thrld, OPT)
            aux[i] = fit
         
        my_runs[run][ch]["Fit"+signal_type] = aux

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False: plt.ioff()
    print("\n")
    return popt
