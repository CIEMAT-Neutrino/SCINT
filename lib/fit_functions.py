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

def sipm_fit(my_runs,OPT):
    print("\n### WELCOME TO THE SCINTILLATION FIT ###")
        
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("EVENTS HAVE NOT BEEN PROCESSED! Please run Process.py")
        return 0

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        for i in range(len(my_runs[run][ch]["ADC"])):
            RAW = ana_runs[run][ch]["P_channel"]*(my_runs[run][ch]["ADC"][i]-ana_runs[run][ch]["Ped_mean"][i])
            RAW_X = 4e-9*np.arange(len(RAW))
            MAX = np.argmax(RAW)

            # output_file = open("scint_fit/"+file+"_CONV.txt","w")

            buffer1     = 100
            buffer2     = 2000
            check       = False
            autozoom    = True
            logy        = True
            thrld       = 1e-1
            term_output = check
            
            for i in range(len(RAW)):
                if RAW[i] <= 1e-10:
                    RAW[i] = 1e-10
                if np.isnan(RAW[i]):
                    RAW[i] = 1e-10

            # output_file = open("scint_fit/"+file+"_FIT.txt","w")
            max_in = np.argmax(RAW)
            guess_t0 = RAW_X[np.argmax(RAW)-10]

            p = np.mean(RAW[:max_in-buffer1])
            # print(pedestal)

            # p = 0.01*pedestal; p_low = pedestal*1e-6; p_high = pedestal*0.5
            t0 = guess_t0; t0_low = guess_t0*0.02; t0_high = guess_t0*50
            sigma = 2e-8; sigma_low = 6e-9; sigma_high = 9e-8
            a1 = 2e-5; a1_low = 1e-8;  a1_high = 9e-2                    
            a2 = 2e-5; a2_low = 1e-8; a2_high = 9e-2                    
            a3 = 2e-5; a3_low = 1e-8; a3_high = 9e-2
            tau1 = 9e-8; tau1_low = 6e-9; tau1_high = 1e-7
            tau2 = 9e-7; tau2_low = tau1_high; tau2_high = 1e-6
            tau3 = 9e-6; tau3_low = tau2_high; tau3_high = 1e-5

            bounds = ([a1_low,sigma_low,tau1_low,t0_low],[a1_high,sigma_high,tau1_high,t0_high])
            initial = (a1,sigma,tau1,t0)
            labels = ["AMP1","SIGM","TAU1","TIME"]

            # FIT PEAK
            # popt, pcov = curve_fit(lambda T,A1,SIGMA,TAU1,T0: func(T,A1,SIGMA,TAU1,T0),RAW_X[max_in-buffer1:-buffer2],RAW[max_in-buffer1:-buffer2],p0 = initial, bounds = bounds, method = "trf")
            popt, pcov = curve_fit(func,RAW_X[max_in-buffer1:-buffer2],RAW[max_in-buffer1:-buffer2],p0 = initial, bounds = bounds, method = "trf")
            # perr1 = np.sqrt(np.diag(pcov))
            # break
            # PRINT FIRST FIT VALUE
            print("\n--- FISRT FIT VALUES (FAST) ---")
            for i in range(len(initial)):
                # print("%s: \t%.2E \u00B1 %.2E"%(labels[i],popt[i],perr1[i]))
                print("%s: \t%.2E"%(labels[i],popt[i]))
            print("-------------------------------")

            # EXPORT FIT PARAMETERS
            a1 = popt[0];sigma = popt[1];tau1 = popt[2];t0 = popt[3]
            sigma2 = sigma*10; sigma2_low = sigma; sigma2_high = sigma*100

            # CHECK FIRST FIT
            plt.ion()
            next_plot = False
            plt.rcParams['figure.figsize'] = [16, 8]
            plt.subplot(1,2,1)
            plt.title("First fit to determine peak")
            plt.plot(RAW_X,RAW,label="RAW")
            plt.plot(RAW_X[max_in-buffer1:max_in+int(buffer1/2)],func(RAW_X[max_in-buffer1:max_in+int(buffer1/2)],*popt),label="FIT")
            # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
            plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
            if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
            plt.legend()

            # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
            bounds2 = ([sigma2_low,a2_low,tau2_low,a3_low,tau3_low],[sigma2_high,a2_high,tau2_high,a3_high,tau3_high])
            initial2 = (sigma2,a2,tau2,a3,tau3)
            labels2 = ["SIGM","AMP2","TAU2","AMP3","TAU3"]
            popt, pcov = curve_fit(lambda T,SIGMA2,A2,TAU2,A3,TAU3: logfunc3(T,p,a1,SIGMA2,tau1,t0,A2,TAU2,A3,TAU3),RAW_X[max_in-buffer1:-buffer2],np.log(RAW[max_in-buffer1:-buffer2]),p0 = initial2, bounds = bounds2, method = "trf")
            perr2 = np.sqrt(np.diag(pcov))

            sigma2 = popt[0];a2 = popt[1];tau2 = popt[2];a3 = popt[3];tau3 = popt[4]
            param = [p,a1,sigma2,tau1,t0,a2,tau2,a3,tau3]

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

            plt.subplot(1,2,2)
            plt.title("Second fit with full wvf")
            plt.plot(RAW_X[max_in-buffer1:],func3(RAW_X[max_in-buffer1:],*param),c="tab:orange",label="FIT")
            plt.plot(RAW_X,RAW,zorder=0,c="tab:blue",label="RAW")
            plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
            # plt.axvline(RAW_X[-buffer2],ls = "--",c = "k")
            if check_key(OPT,"LOGY") != False: plt.semilogy();plt.ylim(thrld,RAW[MAX]*1.1)
            plt.legend()
            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()
            # output_file.close()