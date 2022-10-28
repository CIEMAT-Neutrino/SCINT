import numpy as np
import scipy as sc
import matplotlib.pyplot as plt

from .io_functions import load_npy,load_analysis_npy
from .io_functions import check_key
from scipy.optimize import curve_fit
from scipy.special import erf

from itertools import product

def func(T,A,SIGMA,TAU,T0):
    return (2*A/TAU)*np.exp((SIGMA/(np.sqrt(2)*TAU))**2-(np.array(T)-T0)/TAU)*(1-erf((SIGMA**2-TAU*(np.array(T)-T0))/(np.sqrt(2)*SIGMA*TAU)))

def logfunc3(T,P,A1,SIGMA,TAU1,T0,A2,TAU2,A3,TAU3):
    return np.log(P + func(T,A1,SIGMA,TAU1,T0) + func(T,A2,SIGMA,TAU2,T0) + func(T,A3,SIGMA,TAU3,T0))

def func3(T,P,A1,SIGMA,TAU1,T0,A2,TAU2,A3,TAU3):
    return P + func(T,A1,SIGMA,TAU1,T0) + func(T,A2,SIGMA,TAU2,T0) + func(T,A3,SIGMA,TAU3,T0)

def func2sigma(T,P,A1,SIGMA1,SIGMA2,TAU1,T0,A2,TAU2):
    return P + func(T,A1,SIGMA1,TAU1,T0) + func(T,A2,SIGMA2,TAU2,T0)

def logfunc2sigma(T,P,A1,SIGMA1,SIGMA2,TAU1,T0,A2,TAU2):
    return np.log(P + func(T,A1,SIGMA1,TAU1,T0) + func(T,A2,SIGMA2,TAU2,T0))

def scfunc(T,A,B,C,D,E,F):
    return (A*np.exp(-(T-C)/B)/np.power(2*np.pi,0.5)*np.exp(-D**2/(B**2)))*(1-erf(((C-T)/D+D/B)/np.power(2,0.5)))+(E*np.exp(-(T-C)/F)/np.power(2*np.pi,0.5)*np.exp(-D**2/(F**2)))*(1-erf(((C-T)/D+D/F)/np.power(2,0.5)))

def sipm_fit(my_runs,OPT):
    print("\n### WELCOME TO THE SiPM FIT ###")
        
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("EVENTS HAVE NOT BEEN PROCESSED! Please run Process.py")
        return 0

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        if check_key(OPT, "AVE") != False: AVE = OPT["AVE"]
        else: AVE = "ADC"
        
        for i in range(len(my_runs[run][ch][AVE])):
            if AVE == "ADC": RAW = ana_runs[run][ch]["P_channel"]*(my_runs[run][ch][AVE][i]-ana_runs[run][ch]["Ped_mean"][i])
            else: RAW = my_runs[run][ch][AVE]
            
            RAW_X = 4e-9*np.arange(len(RAW))
            MAX = np.argmax(RAW)
            thrld = 1e-1
            BUFFER = 100
            buffer2 = 2000

            OPT["CUT_NEGATIVE"] == True
            popt1,perr1 = peak_fit(RAW, RAW_X,BUFFER,OPT)

            p = np.mean(RAW[:MAX-BUFFER])
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
            popt, pcov = curve_fit(lambda T,SIGMA2,A2,TAU2,A3,TAU3: logfunc3(T,p,a1,SIGMA2,tau1,popt1[3],A2,TAU2,A3,TAU3),RAW_X[MAX-BUFFER:-buffer2],np.log(RAW[MAX-BUFFER:-buffer2]),p0 = initial2, bounds = bounds2, method = "trf")
            perr2 = np.sqrt(np.diag(pcov))

            sigma2 = popt[0];a2 = popt[1];tau2 = popt[2];a3 = popt[3];tau3 = popt[4]
            param = [p,a1,sigma2,tau1,popt1[3],a2,tau2,a3,tau3]

            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(p,perr1[0]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(t0,perr1[4]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(sigma2,perr2[0]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a1,perr1[1]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau1,perr1[3]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a2,perr2[1]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau2,0))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a3,perr2[2]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau3,0))

            print("\n--- SECOND FIT VALUES (SLOW) ---")
            for i in range(len(initial2)):
                print("%s: \t%.2E \u00B1 %.2E"%(labels2[i],popt[i],perr2[i]))
            print("--------------------------------\n")
            
            try:
                if OPT["SHOW"] == False: continue
                else: pass
            except:
                print("SHOW key not included in OPT")
                # CHECK FIRST FIT
                plt.ion()
                next_plot = False
                plt.rcParams['figure.figsize'] = [16, 8]
                plt.subplot(1,2,1)
                plt.title("First fit to determine peak")
                plt.plot(RAW_X,RAW,label="RAW")
                plt.plot(RAW_X[MAX-BUFFER:MAX+int(BUFFER/2)],func(RAW_X[MAX-BUFFER:MAX+int(BUFFER/2)],*popt1),label="FIT")
                # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
                plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
                if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
                plt.legend()

                plt.subplot(1,2,2)
                plt.title("Second fit with full wvf")
                plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
                plt.plot(RAW_X[MAX-BUFFER:],func3(RAW_X[MAX-BUFFER:],*param),c="tab:orange",label="FIT")
                plt.plot(RAW_X,func3(RAW_X,*param),c="tab:green",label="FIT_FULL_LENGHT")
                plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
                # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
                if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
                plt.legend()
                while not plt.waitforbuttonpress(-1): pass
                plt.clf()
            plt.ioff()

def scint_fit(my_runs,OPT):
    print("\n### WELCOME TO THE SCINTILLATION FIT ###")
        
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("Events have not been processed")

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        if check_key(OPT, "AVE") == True and (OPT["AVE"] == "AvWvf" or OPT["AVE"] == "AvWvf_peak" or OPT["AVE"] == "AvWvf_threshold"): 
            AVE = OPT["AVE"]
            LOOP = 1
        else: 
            AVE = "ADC"
            LOOP = len(my_runs[run][ch][AVE])
        
        for i in range(LOOP):
            
            if AVE == "ADC": RAW = ana_runs[run][ch]["P_channel"]*(my_runs[run][ch][AVE][i]-ana_runs[run][ch]["Ped_mean"][i])
            else: RAW = my_runs[run][ch][AVE]
            
            RAW_X = 4e-9*np.arange(len(RAW))
            MAX = np.argmax(RAW)
            thrld = 1e-1
            BUFFER = 100
            buffer2 = 2000

            OPT["CUT_NEGATIVE"] = True
            popt1,perr1 = peak_fit(RAW, RAW_X,BUFFER,OPT)

            # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
            p = np.mean(RAW[:MAX-BUFFER])
            a1 = 2e-5; a1_low = 1e-8;  a1_high = 9e-2                    
            a2 = 2e-5; a2_low = 1e-8; a2_high = 9e-2                    
            a3 = 2e-5; a3_low = 1e-8; a3_high = 9e-2
            tau1 = 9e-8; tau1_low = 6e-9; tau1_high = 1e-7
            tau2 = 9e-7; tau2_low = tau1_high; tau2_high = 1e-6
            tau3 = 9e-6; tau3_low = tau2_high; tau3_high = 1e-5
            sigma2 = popt1[1]*10; sigma2_low = popt1[1]; sigma2_high = popt1[1]*100
            bounds2 = ([sigma2_low,a3_low,tau3_low],[sigma2_high,a3_high,tau3_high])
            initial2 = (sigma2,a3,tau3)
            labels2 = ["SIG2","AMP2","TAU2"]
            popt, pcov = curve_fit(lambda T,SIGMA2,A3,TAU3: logfunc2sigma(T,p,a1,popt1[1],SIGMA2,tau1,popt1[3],A3,TAU3),RAW_X[MAX-BUFFER:buffer2],np.log(RAW[MAX-BUFFER:buffer2]),p0 = initial2, bounds = bounds2, method = "trf")
            perr2 = np.sqrt(np.diag(pcov))
            sigma2 = popt[0];a3 = popt[1];tau3 = popt[2]
            param = [p,a1,popt1[1],sigma2,tau1,popt1[3],a3,tau3]

            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(p,perr1[0]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(t0,perr1[4]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(sigma2,perr2[0]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a1,perr1[1]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau1,perr1[3]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a2,perr2[1]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau2,0))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(a3,perr2[2]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(tau3,0))

            print("\n--- SECOND FIT VALUES (SLOW) ---")
            for i in range(len(initial2)):
                print("%s: \t%.2E \u00B1 %.2E"%(labels2[i],popt[i],perr2[i]))
            print("--------------------------------\n")

            try:
                if OPT["SHOW"] == False: continue
                else: pass
            except:
                print("SHOW key not included in OPT")
                # CHECK FIRST FIT
                plt.ion()
                next_plot = False
                plt.rcParams['figure.figsize'] = [16, 8]
                plt.subplot(1,2,1)
                plt.title("First fit to determine peak")
                plt.plot(RAW_X,RAW,label="RAW")
                plt.plot(RAW_X[MAX-BUFFER:MAX+int(BUFFER/2)],func(RAW_X[MAX-BUFFER:MAX+int(BUFFER/2)],*popt1),label="FIT")
                # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
                plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
                if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
                plt.legend()
                plt.subplot(1,2,2)
                plt.title("Second fit with full wvf")
                plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
                plt.plot(RAW_X[MAX-BUFFER:],func2sigma(RAW_X[MAX-BUFFER:],*param),c="tab:orange",label="FIT")
                plt.plot(RAW_X,func2sigma(RAW_X,*param),c="tab:green",label="FIT_FULL_LENGHT")
                plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
                # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
                if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
                plt.legend()
                while not plt.waitforbuttonpress(-1): pass
                plt.clf()
            plt.ioff()

def sc_fit(my_runs,OPT):
    print("\n### WELCOME TO THE SC FIT ###")        
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("Events have not been processed")

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        if check_key(OPT, "AVE") == True and (OPT["AVE"] == "AvWvf" or OPT["AVE"] == "AvWvf_peak" or OPT["AVE"] == "AvWvf_threshold"): 
            AVE = OPT["AVE"]
            LOOP = 1
        else: 
            AVE = "ADC"
            LOOP = len(my_runs[run][ch][AVE])
        
        for i in range(LOOP):
            if AVE == "ADC": RAW = ana_runs[run][ch]["P_channel"]*(my_runs[run][ch][AVE][i]-ana_runs[run][ch]["Ped_mean"][i])
            else: RAW = my_runs[run][ch][AVE]

            FIT_RAW_X = np.arange(len(RAW))
            RAW_X = 4e-9*FIT_RAW_X
            MAX = np.argmax(RAW)

            try:
                if OPT["SHOW"] == False: continue
                else: pass
            except:
                print("'SHOW' key not included in OPT")

            # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
            t0 = np.argmax(RAW)
            initial = (500,1000,t0,20,-500,1000)
            labels = ["AMP","TAU1","T0","SIGMA","AMP2","TAU2"]

            popt, pcov = curve_fit(scfunc,FIT_RAW_X,RAW,p0 = initial, method = "trf")
            perr = np.sqrt(np.diag(pcov))

            print("\n--- FIT VALUES (SLOW) ---")
            for i in range(len(initial)):
                print("%s: \t%.2E \u00B1 %.2E"%(labels[i],popt[i],perr[i]))
            print("--------------------------------\n")

            plt.ion()
            next_plot = False
            plt.rcParams['figure.figsize'] = [8, 8]
            plt.title("Fit with full wvf")
            plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
            plt.plot(RAW_X,scfunc(FIT_RAW_X,*popt),"tab:orange",label="FIT")
            plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
            if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True: 
                plt.semilogy()
                plt.ylim(thrld,RAW[MAX]*1.1)
            
            plt.legend()
            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()

def peak_fit(FIT_RAW,RAW_X,BUFFER,OPT):

    MAX = np.argmax(FIT_RAW)

    # output_file = open("scint_fit/"+file+"_CONV.txt","w")

    # BUFFER     = 100
    buffer2     = 2000
    check       = False
    autozoom    = True
    thrld       = 1e-1
    
    if check_key(OPT, "CUT_NEGATIVE") == True and OPT["CUT_NEGATIVE"] == True:
        for i in range(len(FIT_RAW)):
            if FIT_RAW[i] <= 1e-10:
                FIT_RAW[i] = 1e-10
            if np.isnan(FIT_RAW[i]):
                FIT_RAW[i] = 1e-10

    # output_file = open("scint_fit/"+file+"_FIT.txt","w")
    guess_t0 = RAW_X[np.argmax(FIT_RAW)-10]
    p = np.mean(FIT_RAW[:MAX-BUFFER])

    t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
    sigma = 2e-8; sigma_low = 6e-9; sigma_high = 9e-8
    a1 = 2e-5; a1_low = 1e-8;  a1_high = 9e-2                    
    tau1 = 9e-8; tau1_low = 6e-9; tau1_high = 1e-7
    bounds = ([a1_low,sigma_low,tau1_low,t0_low],[a1_high,sigma_high,tau1_high,t0_high])
    initial = (a1,sigma,tau1,t0)
    labels = ["AMP1","SIG1","TAU1","TIME"]

    # FIT PEAK
    popt, pcov = curve_fit(func,RAW_X[MAX-BUFFER:-buffer2],FIT_RAW[MAX-BUFFER:-buffer2],p0 = initial, bounds = bounds, method = "trf")
    perr1 = np.sqrt(np.diag(pcov))

    # PRINT FIRST FIT VALUE
    print("\n--- FISRT FIT VALUES (FAST) ---")
    for i in range(len(initial)):
        print("%s: \t%.2E \u00B1 %.2E"%(labels[i],popt[i],perr1[i]))
    print("-------------------------------")

    # EXPORT FIT PARAMETERS
    a1 = popt[0];sigma = popt[1];tau1 = popt[2];t0 = popt[3]

    return popt,perr1