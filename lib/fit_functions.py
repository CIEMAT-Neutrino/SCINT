import numpy as np
import scipy as sc
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.special import erf

from .io_functions import load_npy,check_key

from itertools import product

def gaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
    return y

def loggaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
    return np.log10(y)

def gaussian(x, height, center, width):
    return height*np.exp(-(x - center)**2/(2*width**2))

def loggaussian(x, height, center, width):
    return np.log10(gaussian(x, height, center, width))

def func(T,T0,SIGMA,A,TAU):
    return (2*A/TAU)*np.exp((SIGMA/(np.sqrt(2)*TAU))**2-(np.array(T)-T0)/TAU)*(1-erf((SIGMA**2-TAU*(np.array(T)-T0))/(np.sqrt(2)*SIGMA*TAU)))

def func2(T,P,T0,SIGMA,A1,TAU1,A2,TAU2):
    return P + func(T,T0,SIGMA,A1,TAU1) + func(T,T0,SIGMA,A2,TAU2)

def logfunc2(T,P,T0,SIGMA,A1,TAU1,A2,TAU2):
    return np.log(P + func(T,T0,SIGMA,A1,TAU1) + func(T,T0,SIGMA,A2,TAU2))

def logfunc3(T,P,T0,SIGMA,A1,TAU1,A2,TAU2,A3,TAU3):
    return np.log(P + func(T,T0,SIGMA,A1,TAU1) + func(T,T0,SIGMA,A2,TAU2) + func(T,T0,SIGMA,A3,TAU3))

def func3(T,P,T0,SIGMA,A1,TAU1,A2,TAU2,A3,TAU3):
    return P + func(T,T0,SIGMA,A1,TAU1) + func(T,T0,SIGMA,A2,TAU2) + func(T,T0,SIGMA,A3,TAU3)

def scfunc(T,A,B,C,D,E,F):
    return (A*np.exp(-(T-C)/B)/np.power(2*np.pi,0.5)*np.exp(-D**2/(B**2)))*(1-erf(((C-T)/D+D/B)/np.power(2,0.5)))+(E*np.exp(-(T-C)/F)/np.power(2*np.pi,0.5)*np.exp(-D**2/(F**2)))*(1-erf(((C-T)/D+D/F)/np.power(2,0.5)))

def sipm_fit(RAW,RAW_X,FIT_RANGE,THRLD=1e-6,OPT={}):
    MAX = np.argmax(RAW)
    # THRLD = 1e-4
    BUFFER1 = FIT_RANGE[0]
    BUFFER2 = FIT_RANGE[1]

    OPT["CUT_NEGATIVE"] = True
    popt1,perr1 = peak_fit(RAW, RAW_X,BUFFER1,OPT)

    p = np.mean(RAW[:MAX-BUFFER1])
    a1 = 2e-5; a1_low = 1e-8;  a1_high = 9e-2                    
    a2 = 2e-5; a2_low = 1e-8; a2_high = 9e-2                    
    a3 = 2e-5; a3_low = 1e-8; a3_high = 9e-2
    tau1 = 9e-8; tau1_low = 6e-9; tau1_high = 1e-7
    tau2 = 9e-7; tau2_low = tau1_high; tau2_high = 1e-6
    tau3 = 9e-6; tau3_low = tau2_high; tau3_high = 1e-5
    sigma2 = popt1[1]*10; sigma2_low = popt1[1]; sigma2_high = popt1[1]*100

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    bounds2 = ([sigma2_low,a2_low,tau2_low,a3_low,tau3_low],[sigma2_high,a2_high,tau2_high,a3_high,tau3_high])
    initial2 = (sigma2,a2,tau2,a3,tau3)
    labels2 = ["SIGM","AMP2","TAU2","AMP3","TAU3"]
    popt, pcov = curve_fit(lambda T,SIGMA2,A2,TAU2,A3,TAU3: logfunc3(T,p,popt1[0],SIGMA2,popt1[2],popt1[3],A2,TAU2,A3,TAU3),RAW_X[MAX-BUFFER1:MAX+BUFFER2],np.log(RAW[MAX-BUFFER1:MAX+BUFFER2]),p0 = initial2, bounds = bounds2, method = "trf")
    perr2 = np.sqrt(np.diag(pcov))

    sigma2 = popt[0];a2 = popt[1];tau2 = popt[2];a3 = popt[3];tau3 = popt[4]
    param = [p,a1,sigma2,tau1,popt1[3],a2,tau2,a3,tau3]
    if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
        print("\n--- SECOND FIT VALUES (SLOW) ---")
        for i in range(len(initial2)):
            print("%s: \t%.2E \u00B1 %.2E"%(labels2[i],popt[i],perr2[i]))
        print("--------------------------------\n")

        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1,2,1)
        plt.title("First fit to determine peak")
        plt.plot(RAW_X,RAW,label="RAW")
        plt.plot(RAW_X[MAX-BUFFER1:MAX+int(BUFFER1/2)],func(RAW_X[MAX-BUFFER1:MAX+int(BUFFER1/2)],*popt1),label="FIT")
        # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(THRLD,RAW[MAX]*1.1)
        plt.legend()

        plt.subplot(1,2,2)
        plt.title("Second fit with full wvf")
        plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
        plt.plot(RAW_X[MAX-BUFFER1:MAX+BUFFER2],func3(RAW_X[MAX-BUFFER1:MAX+BUFFER2],*param),c="tab:orange",label="FIT")
        plt.plot(RAW_X,func3(RAW_X,*param),c="tab:green",label="FIT_FULL_LENGHT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
        if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(THRLD,RAW[MAX]*1.1)
        plt.legend()

    while not plt.waitforbuttonpress(-1): pass
    plt.clf()
    aux = func3(RAW_X,*param)
    plt.ioff()
    return aux

def scint_fit(RAW,RAW_X,FIT_RANGE,THRLD=1e-6,OPT={}):        
    next_plot = False
    MAX = np.argmax(RAW)
    # THRLD = 1e-10
    BUFFER1 = FIT_RANGE[0]
    BUFFER2 = FIT_RANGE[1]

    OPT["CUT_NEGATIVE"] = True
    popt1,perr1 = peak_fit(RAW,RAW_X,BUFFER1,THRLD,OPT)

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    p = np.mean(RAW[:MAX-BUFFER1])

    sigm = popt1[1]; sigm_low = sigm*0.9; sigm_high = sigm*1.1
    a1   = popt1[2]; a1_low   = a1*0.9;   a1_high   = a1*1.1  
    tau1 = popt1[3]; tau1_low = tau1*0.9; tau1_high = tau1*1.1  

    a2 =   2e-8;   a2_low = 6e-9;   a2_high = 9e-4
    tau2 = 8e-7; tau2_low = 5e-7; tau2_high = 1e-6
    
    bounds2 = ([sigm_low,a1_low,tau1_low,a2_low,tau2_low],[sigm_high,a1_high,tau1_high,a2_high,tau2_high])
    initial2 = (sigm,a1,tau1,a2,tau2)
    labels2 = ["SIGM","AMP1","TAU1","AMP2","TAU2"]

    try:
        popt2, pcov2 = curve_fit(lambda T,SIGMA,A1,TAU1,A2,TAU2: logfunc2(T,p,popt1[0],SIGMA,A1,TAU1,A2,TAU2),RAW_X[MAX-BUFFER1:MAX+BUFFER2],np.log(RAW[MAX-BUFFER1:MAX+BUFFER2]),p0 = initial2, bounds = bounds2, method = "trf")
        # popt2, pcov2 = curve_fit(lambda T,SIGMA,A1,TAU1,A2,TAU2: func2(T,p,popt1[0],SIGMA,A1,TAU1,A2,TAU2),RAW_X[MAX-BUFFER1:MAX+BUFFER2],np.log(RAW[MAX-BUFFER1:MAX+BUFFER2]),p0 = initial2, bounds = bounds2, method = "trf")
        perr2 = np.sqrt(np.diag(pcov2))
    except:
        print("Fit could not be performed")
        popt2 = initial2
        perr2 = np.zeros(len(popt2))

    t0 = popt1[0]   ; a1 = popt2[1] ; tau1 = popt2[2]
    sigma = popt2[0]; a2 = popt2[3] ; tau2 = popt2[4]
    
    param = [p,t0,sigma,a1,tau1,a2,tau2]
    
    if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
        if check_key(OPT,"COLOR") == True: color = OPT["COLOR"]
        else: color = "tab:red"
        print("\n--- SECOND FIT VALUES (SLOW) ---")
        for i in range(len(initial2)):
            print("%s:\t%.2E\t%.2E"%(labels2[i],popt2[i],perr2[i]))
        print("--------------------------------\n")

        # print("SHOW key not included in OPT")
        # CHECK FIRST FIT
        plt.rcParams['figure.figsize'] = [16, 8]
        plt.subplot(1,2,1)
        plt.title("First fit to determine peak")
        plt.plot(RAW_X,RAW,label="RAW",c=color)
        plt.plot(RAW_X[MAX-BUFFER1:MAX+int(BUFFER1/2)],func(RAW_X[MAX-BUFFER1:MAX+int(BUFFER1/2)],*popt1),label="FIT")
        # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True: plt.semilogy();plt.ylim(THRLD,RAW[MAX]*1.1)
        plt.legend()

        plt.subplot(1,2,2)
        plt.title("Second fit with full wvf")
        plt.plot(RAW_X,RAW,zorder=0,label="RAW",c=color)
        plt.plot(RAW_X[MAX-BUFFER1:MAX+BUFFER2],func2(RAW_X[MAX-BUFFER1:MAX+BUFFER2],*param),label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        plt.axvline(RAW_X[MAX+BUFFER2],ls = "--",c = "k")
        if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True: plt.semilogy();plt.ylim(THRLD,RAW[MAX]*1.1)
        plt.legend()

    while not plt.waitforbuttonpress(-1): pass
    plt.clf()
    aux = func2(RAW_X,*param)
    return aux

def sc_fit(RAW,RAW_X,FIT_RANGE,THRLD=1e-6,OPT={}):
    # plt.ion()
    # THRLD = 1e-10
    next_plot = False
    plt.rcParams['figure.figsize'] = [8, 8]
    FIT_RAW_X = np.arange(len(RAW))
    MAX = np.argmax(RAW)

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    t0 = np.argmax(RAW)
    initial = (1500,150,t0,8,-700,300)
    # bounds = ([-200,10,t0*0.1,1,-1500,10],[10000,3000,t0*10,20,1500,1000])
    labels = ["AMP","TAU1","T0","SIGMA","AMP2","TAU2"]

    try:
        popt, pcov = curve_fit(scfunc,FIT_RAW_X,RAW,p0 = initial,method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except:
        print("Fit did not succeed")
        popt = initial
        perr = np.zeros(len(initial))

    if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
        print("\n--- FIT VALUES (SLOW) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i],popt[i],perr[i]))
        print("--------------------------------\n")

        plt.title("Fit with full wvf")
        plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
        plt.plot(RAW_X,scfunc(FIT_RAW_X,*popt),"tab:orange",label="FIT")
        plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
        if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True: 
            plt.semilogy()
            plt.ylim(THRLD,RAW[MAX]*1.1)
        plt.legend()

    while not plt.waitforbuttonpress(-1): pass
    plt.clf()
    aux = scfunc(FIT_RAW_X,*popt)
    # print("\n")
    return aux

def peak_fit(FIT_RAW,RAW_X,BUFFER,THRLD,OPT):
    MAX = np.argmax(FIT_RAW)
    # print(FIT_RAW)
    if check_key(OPT, "CUT_NEGATIVE") == True and OPT["CUT_NEGATIVE"] == True:
        for i in range(len(FIT_RAW)):
            if FIT_RAW[i] <= THRLD:
                FIT_RAW[i] = THRLD
            if np.isnan(FIT_RAW[i]):
                FIT_RAW[i] = THRLD

    guess_t0 = RAW_X[np.argmax(FIT_RAW)-10]
    p = np.mean(FIT_RAW[:MAX-BUFFER])

    t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
    
    sigma = 1e-8; sigma_low = 6e-9; sigma_high = 9e-6
    a1 =    5e-8;    a1_low = 1e-9;    a1_high = 9e-6                    
    tau1 =  1e-8;  tau1_low = 6e-9;  tau1_high = 1e-6

    bounds = ([t0_low,sigma_low,a1_low,tau1_low],[t0_high,sigma_high,a1_high,tau1_high])
    initial = (t0,sigma,a1,tau1)
    labels = ["TIME","SIGM","AMP1","TAU1"]

    # FIT PEAK
    try:
        popt, pcov = curve_fit(func,RAW_X[MAX-BUFFER:MAX+int(BUFFER/2)],FIT_RAW[MAX-BUFFER:MAX+int(BUFFER/2)],p0 = initial, bounds = bounds, method = "trf")
        perr = np.sqrt(np.diag(pcov))
    except:
        print("Peak fit could not be performed")
        popt = initial
        perr = np.zeros(len(initial))

    # PRINT FIRST FIT VALUE
    if check_key(OPT,"SHOW") == True and OPT["SHOW"] == True:
        print("\n--- FISRT FIT VALUES (FAST) ---")
        for i in range(len(initial)):
            print("%s:\t%.2E\t%.2E"%(labels[i],popt[i],perr[i]))
        print("-------------------------------")

    # EXPORT FIT PARAMETERS
    # a1 = popt[2];sigma = popt[1];tau1 = popt[3];t0 = popt[0]

    return popt,perr

def fit_wvfs(my_runs,signal_type,THRLD,FIT_RANGE=[0,0],KEYS=["ADC"],OPT={}):
    plt.ion()
    for run,ch,key in product(my_runs["N_runs"],my_runs["N_channels"],KEYS):
        aux = dict()
        if key.startswith("Dec"): OPT["COLOR"] = "tab:red"
        RAW = my_runs[run][ch][key]        
        RAW_X = my_runs[run][ch]["Sampling"]*np.arange(len(RAW[0]))
        # print(RAW)
        for i in range(len(RAW)):
            print("Fitting wvf ",i)
            # print(RAW[i])
            if check_key(OPT, "NORM") == True and OPT["NORM"] == True: RAW[i] = RAW[i]/np.max(RAW[i])
            if signal_type == "SiPM":  fit = sipm_fit(RAW[i],RAW_X,FIT_RANGE,THRLD,OPT)
            if signal_type == "SCINT": fit = scint_fit(RAW[i],RAW_X,FIT_RANGE,THRLD,OPT)
            if signal_type == "SC":    fit = sc_fit(RAW[i],RAW_X,FIT_RANGE,THRLD,OPT)
            aux[i] = fit
        
       
        my_runs[run][ch]["Fit_"+signal_type] = aux
        # aux_path=PATH+"Fit_run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
        
        try:
            del my_runs[run][ch]["ADC"]
        except:
            print("'ADC' branch has already been deleted")

    plt.ioff()
    print("\n")
