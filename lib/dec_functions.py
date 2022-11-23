import numpy as np
from curve import Curve
import matplotlib.pyplot as plt

from .io_functions import check_key
from .fit_functions import func2
from .wvf_functions import smooth,find_baseline_cuts

import scipy.interpolate
from scipy.optimize import curve_fit
from itertools import product

def conv_func2(wvf,T0,SIGMA,TAU1,A1,TAU2,A2):

    resp = func2(wvf[0],0,T0,SIGMA,A1,TAU1,A2,TAU2)
    
    conv = convolve(wvf[1],resp)
    conv = conv/np.max(conv)
    wvf_max = np.argmax(wvf[1])
    conv_max = np.argmax(conv)
    return conv[conv_max-wvf_max:conv_max+len(wvf[1])-wvf_max]

def logconv_func2(wvf,T0,SIGMA,TAU1,A1,TAU2,A2):
    
    resp = logfunc2(wvf[0],0,T0,SIGMA,A1,TAU1,A2,TAU2)

    conv = convolve(wvf[1],resp)
    conv = conv/np.max(conv)
    wvf_max = np.argmax(wvf[1])
    conv_max = np.argmax(conv)
    return conv[conv_max-wvf_max:conv_max+len(wvf[1])-wvf_max]

def gauss(X,STD,N,MEAN=0,NORM=1):
    A=1
    if NORM=="standard":
        A=1/(STD*np.sqrt(2*np.pi))
    else:
        A=NORM
    Y=A*np.exp(-(X-MEAN)**N/(2*STD**N))
    return Y

def fit_gauss(X,STD,N,MEAN=0,NORM=1):
    return np.log10(gauss(X,STD,N,MEAN=0,NORM=1))

def deconvolve(my_runs,dec_runs,out_runs,KEY=[],OPT={}):
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        aux = dict()
        TRIMM = 0
        
        CLEAN = dec_runs[run][ch][KEY[1]][0]
        for i in range(len(my_runs[run][ch][KEY[0]])):
            # Select required runs and parameters

            RAW = my_runs[run][ch][KEY[0]][i]
            
            # Roll signal to align wvfs
            rollcount = 0
            while np.argmax(RAW) < np.argmax(CLEAN):
                RAW = np.roll(RAW,1)    
                rollcount = rollcount + 1

            # Check if arrays have the same length
            if len(CLEAN) < len(RAW):
                RAW = RAW[:-(len(RAW)-len(CLEAN))]
            if len(CLEAN) > len(RAW):
                CLEAN = CLEAN[:-(len(CLEAN)-len(RAW))] 

            # Can be used for test to trimm array
            if check_key(OPT, "TRIMM") == True: TRIMM = OPT["TRIMM"]
            if check_key(OPT, "AUTO_TRIMM") == True and OPT["AUTO_TRIMM"] == True:
                j = 0
                while 2**j < len(RAW):
                    j = j+1

                TRIMM = len(RAW)-2**(j-1)

            if TRIMM != 0: 
                SIGNAL = RAW[rollcount:-TRIMM]
                KERNEL = CLEAN[rollcount:-TRIMM]
                # print("Array length after trimming = %i vs detector response = %i"%(len(SIGNAL),len(KERNEL)))
            
            else: 
                SIGNAL = RAW[rollcount:]
                KERNEL = CLEAN[rollcount:]
  
                # print("Array length after trimming = %i vs detector response = %i"%(len(SIGNAL),len(KERNEL)))
            
            if len(SIGNAL) % 2 > 0:
                SIGNAL = SIGNAL[:-1]
            if len(KERNEL) % 2 > 0:
                KERNEL = KERNEL[:-1]
            
            # print(KERNEL)
            if check_key(OPT, "SMOOTH") == True:
                if OPT["SMOOTH"] > 0:
                    SIGNAL = smooth(SIGNAL,OPT["SMOOTH"])
                else:
                    print("Invalid value encountered in smooth")
            try:
                STD = my_runs[run][ch]["Ped_STD"][i]
            except:
                STD = np.std(RAW)

            TIMEBIN = my_runs[run][ch]["Sampling"]
            if check_key(OPT,"TIMEBIN") == True: TIMEBIN = OPT["TIMEBIN"]    
            X = TIMEBIN*np.arange(len(SIGNAL))

            # Define noise (should be imported in future iterations)
            NOISE_AMP = 1
            if check_key(OPT, "NOISE_AMP") == True: NOISE_AMP = OPT["NOISE_AMP"]
            NOISE = NOISE_AMP*STD*np.random.randn(len(SIGNAL))
            FFT_NOISE = np.fft.rfft(NOISE)
            
            # Calculate FFT arrays
            FFT_SIGNAL = np.fft.rfft(SIGNAL)
            FFT_SIGNAL_X = np.fft.rfftfreq(len(SIGNAL),4e-9)
           
            i_kernel,f_kernel = find_baseline_cuts(KERNEL)
            FFT_KERNEL = np.fft.rfft(KERNEL)
            WIENER = abs(FFT_KERNEL)**2/(abs(FFT_KERNEL)**2+abs(FFT_NOISE)**2)
            
            # FFT_KERNEL = np.fft.rfft(KERNEL/np.sum(KERNEL[i_kernel:f_kernel]))

            if check_key(OPT,"NORM_DET_RESPONSE") == True and OPT["NORM_DET_RESPONSE"] == True:
                FFT_KERNEL = (FFT_KERNEL/np.max(FFT_KERNEL))
            FFT_KERNEL_X = np.fft.rfftfreq(len(KERNEL),4e-9)
            
            # Interpolate wiener envelop for fit of gaussian filter
            WIENER_BUFFER = 800
            if check_key(OPT,"WIENER_BUFFER") == True: WIENER_BUFFER = OPT["WIENER_BUFFER"]
            WIENER_CURVE = Curve(FFT_KERNEL_X[:-WIENER_BUFFER],(-1*WIENER[:-WIENER_BUFFER])+2)
            ENV = WIENER_CURVE.envelope2(tc=1e6)
            ENV_WIENER = scipy.interpolate.interp1d(ENV.x, ENV.y)
            ENV_WIENER_Y = ENV_WIENER(FFT_SIGNAL_X[:-WIENER_BUFFER])
            ENV_WIENER_MIN = np.argmin(-1*(ENV_WIENER_Y-2))

            # Select fit parameters and perform fit to determin cut-off
            p0 = [50,1.999999]
            lim = [[10,1],[500,8]]
            if check_key(OPT,"FIX_EXP") == True and OPT["FIX_EXP"] == True:
                lim = [[10,1.99999],[2000,2]]
            
            try:
                params,cov=curve_fit(fit_gauss, np.arange(len(FFT_SIGNAL_X))[:ENV_WIENER_MIN], np.log10(-1*(ENV_WIENER_Y[:ENV_WIENER_MIN]-2)),p0=p0,bounds=lim)
            except:
                params = p0
                print("FIT COULD NOT BE PERFORMED!")
            # print("Filter strengh %f and exp %f"%(params[0],params[1]))
            
            # Generate gauss filter and filtered signal
            FFT_GAUSS = gauss(np.arange(len(FFT_SIGNAL)),*params)
            if check_key(OPT, "PRO_RODRIGO") == True and OPT["PRO_RODRIGO"] == True:
                FFT_GAUSS[0] = 0
            
            FFT_GAUSS_SIGNAL = FFT_SIGNAL*FFT_GAUSS
            GAUSS_SIGNAL = np.fft.irfft(FFT_GAUSS_SIGNAL)
            
            # Generate deconvoluted function
            FFT_DEC = FFT_GAUSS_SIGNAL/np.array(FFT_KERNEL)
            # FFT_DEC = np.max(FFT_SIGNAL)*FFT_DEC/np.max(FFT_DEC)
            DEC = np.fft.irfft(FFT_DEC)
            # DEC = np.fft.irfft(FFT_DEC)/np.abs(np.trapz(KERNEL,X))
            if check_key(OPT, "REVERSE") == True and OPT["REVERSE"] == True: DEC = DEC[::-1]
            DEC = np.roll(DEC,np.argmax(KERNEL)) # Roll the function to match original position
            
            DEC_STD = np.mean(DEC[:np.argmax(DEC)-10])
            DEC = DEC-DEC_STD

            #-------------------------------------------------------------------------------------------------------------------
            # Plot results: left shows process in time space; right in frequency space.
            #-------------------------------------------------------------------------------------------------------------------
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
                plt.ion()
                next_plot = False
                plt.rcParams['figure.figsize'] = [16, 8]
                plt.subplot(1,2,1)
                
                i_signal,f_signal = find_baseline_cuts(SIGNAL)
                i_signal,f_signal = find_baseline_cuts(SIGNAL)
                i_resp,f_resp = find_baseline_cuts(KERNEL)
                i_dec,f_dec = find_baseline_cuts(DEC)
                
                if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
                    plt.plot(X,SIGNAL/np.max(SIGNAL),label = "SIGNAL: int = %.4E" %(np.trapz(SIGNAL[i_signal:f_signal],X[i_signal:f_signal])),c="tab:blue",drawstyle="steps")
                    plt.plot(X,GAUSS_SIGNAL/np.max(GAUSS_SIGNAL), label = "GAUSS_SIGNAL: int = %.4E" %(np.trapz(GAUSS_SIGNAL[i_signal:f_signal],X[i_signal:f_signal])),c="blue")
                    plt.plot(X,KERNEL/np.max(KERNEL), label = "DET_RESPONSE: int = %.4E" %(np.trapz(KERNEL[i_resp:f_resp],X[i_resp:f_resp])),c="tab:orange",drawstyle="steps")
                    plt.plot(X,DEC/np.max(DEC),label = "DECONVOLUTION: int = %.2f PE" %(np.sum(DEC[i_dec:f_dec])),c="tab:red",drawstyle="steps",lw=2.)
                else:
                    plt.plot(X,SIGNAL,label = "SIGNAL: int = %.4E" %(np.trapz(SIGNAL[i_signal:f_signal],X[i_signal:f_signal])),c="tab:blue",drawstyle="steps")
                    plt.plot(X,GAUSS_SIGNAL, label = "GAUSS_SIGNAL: int = %.4E" %(np.trapz(GAUSS_SIGNAL[i_signal:f_signal],X[i_signal:f_signal])),c="blue")
                    plt.plot(X,KERNEL, label = "DET_RESPONSE: int = %.4E" %(np.trapz(KERNEL[i_resp:f_resp],X[i_resp:f_resp])),c="tab:orange",drawstyle="steps")
                    plt.plot(X,DEC,label = "DECONVOLUTION: int = %.2f PE" %(np.sum(DEC[i_dec:f_dec])),c="tab:red",drawstyle="steps",lw=2.)
                
                plt.axhline(0,label="Total # PE in deconvolved signal %f"%np.sum(DEC),c="black",alpha=0.5,ls="--")
                print("\nDECONVOLUTION: baseline int =\t %.2f PE" %(np.sum(DEC[i_dec:f_dec])))
                print("DECONVOLUTION: total int =\t %.2f PE\n"%np.sum(DEC))
                plt.axhline(0,c="black",alpha=0.5,ls="--")
                # print("# PE in deconvolved signal %f"%np.sum(DEC[i_dec:f_dec]))
                
                plt.ylabel("ADC Counts");plt.xlabel("Time in [s]")
                if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True:
                    if check_key(OPT,"THRLD") == True: THRLD = OPT["THRLD"]
                    else: THRLD = 1e-6
                    plt.semilogy()
                    plt.ylim(THRLD)
                if check_key(OPT,"FOCUS") == True and OPT["FOCUS"] == True: 
                    plt.xlim(4e-9*np.array([np.argmax(SIGNAL)-100,np.argmax(SIGNAL)+1000]))
                    plt.ylim([np.min(SIGNAL)*1.1,np.max(DEC)*1.1])
                plt.legend()
                
                plt.subplot(1,2,2)
                if check_key(OPT,"SHOW_F_SIGNAL") != False: plt.plot(FFT_SIGNAL_X,np.abs(FFT_SIGNAL),label = "SIGNAL",c="tab:blue")
                if check_key(OPT,"SHOW_F_GSIGNAL") != False: plt.plot(FFT_SIGNAL_X,np.abs(FFT_GAUSS_SIGNAL),label = "GAUSS_SIGNAL",c="blue")
                if check_key(OPT,"SHOW_F_DET_RESPONSE") != False: plt.plot(FFT_KERNEL_X,np.abs(FFT_KERNEL),label = "DET_RESPONSE",c="tab:orange")
                
                if check_key(OPT,"SHOW_F_DEC") != False: plt.plot(FFT_SIGNAL_X,np.abs(FFT_DEC),label = "DECONVOLUTION",c="tab:red")
                if check_key(OPT,"SHOW_F_WIENER") != False: 
                    plt.plot(FFT_SIGNAL_X,WIENER,label = "WIENER",c="tab:green")
                    plt.plot(ENV_WIENER.x[:ENV_WIENER_MIN],-1*(ENV_WIENER.y[:ENV_WIENER_MIN]-2),label = "ENV_WIENER",c="tab:pink",ls="--")

                if check_key(OPT,"SHOW_F_GAUSS") != False: plt.plot(FFT_SIGNAL_X,FFT_GAUSS,label = "GAUSS",c="k",ls="--")
                plt.ylabel("a.u.");plt.xlabel("Frequency in [Hz]")
                plt.ylim(1e-12,np.max(FFT_SIGNAL)*100)
                plt.semilogy();plt.semilogx()
                plt.legend()

                while not plt.waitforbuttonpress(-1): pass
                plt.clf()
            aux[i] = DEC
        plt.ioff()

        out_runs[run][ch][KEY[2]] = aux
        print("Generated wvfs with key %s"%KEY[2])
    # return aux,X

def convolve():
    print("\n### WELCOME TO THE CONVOLUTION STUDIES ###\n")

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        aux = dict()
    
        for i in range(len(my_runs[run][ch][KEY[0]])):
            # Select required runs and parameters

            RAW = my_runs[run][ch][KEY[0]][i]

            TIMEBIN = my_runs[run][ch]["Sampling"]
            if check_key(OPT,"TIMEBIN") == True: TIMEBIN = OPT["TIMEBIN"]    
            X = TIMEBIN*np.arange(len(SIGNAL))

            ########################################################################
            #_____________________CONVOLUTION_AND_FIT_PARAMETERS___________________#
            ########################################################################

            # MUON SC CONFIG
            t_fast   = 2e-8; t_fast_low   = 1e-8; t_fast_high   = 4e-8
            t_slow   = 1e-6; t_slow_low   = 6e-7; t_slow_high   = 5e-6
            amp_fast = 2e-8; amp_fast_low = 1e-8; amp_fast_high = 3e-8
            amp_slow = 5e-8; amp_slow_low = 1e-8; amp_slow_high = 9e-8
            sigma    = 2e-8; sigma_low    = 9e-9; sigma_high    = 3e-8

            # MUON SiPM CONFIG
            t_fast   = 2e-8; t_fast_low   = 1e-8; t_fast_high   = 4e-8
            t_slow   = 1.2e-6; t_slow_low   = 1e-6; t_slow_high   = 5e-6
            amp_fast = 2e-8; amp_fast_low = 1e-8; amp_fast_high = 3e-8
            amp_slow = 2e-8; amp_slow_low = 8e-9; amp_slow_high = 9e-8
            sigma    = 2e-8; sigma_low    = 9e-9; sigma_high    = 3e-8

            fit_initials = (t_fast,t_slow,amp_fast,amp_slow,sigma)
            fit_finals = [t_fast,t_slow,amp_fast,amp_slow,sigma]
            limits_low = [t_fast_low,t_slow_low,amp_fast_low,amp_slow_low,sigma_low]
            limits_high = [t_fast_high,t_slow_high,amp_fast_high,amp_slow_high,sigma_high]
            fit_limits = (limits_low,limits_high)

            popt, pcov = curve_fit(conv_func2,[laser.wvf_x[:-limit],laser.wvf[:-limit]],alpha.wvf[:-limit], p0 = fit_initials, bounds = fit_limits,method="trf")
            perr = np.sqrt(np.diag(pcov))
            conv = conv_func2([laser.wvf_x[:-limit],laser.wvf[:-limit]],*popt)
            func = func2(alpha.wvf_x,*popt)
            conv_int,f_conv,i_conv = signal_int("CONV FUNC",func2(np.arange(0,alpha.wvf_x[-1],5e-10),*popt),timebin,"SiPM","ALL",th = thrld,out = True)

            labels = ["TFAST","TSLOW","AFAST","ASLOW","SIGMA"]
            print("\n--- FIT VALUES ---")
            for i in range(len(fit_initials)):
                fit_finals[i] = popt[i]
                print("%s: %.2E \u00B1 %.2E"%(labels[i],popt[i],perr[i]))
            print("------------------\n")

            print("SLOW = %.2f%%"%(100*popt[3]/(popt[3]+popt[2])))

            ########################################################################
            #________________________PLOT_FIRST_RESULT_____________________________#
            ########################################################################

            # fig1, axs = plt.subplots(2, 1, sharex=True)

            fig1, axs = plt.subplots(2, 1)
            plt.title(decon_runs)
            fig1.subplots_adjust(hspace=0.25)
            fig1.set_figheight(6)
            fig1.set_figwidth(6)

            # axs[0] = plt.subplot2grid(shape=(1, 1), loc=(0, 0), colspan=3)
            # axs[1] = plt.subplot2grid(shape=(1, 1), loc=(3, 0), colspan=3)

            axs[0].plot(laser.wvf_x,laser.wvf,label = label_luz)
            axs[0].plot(alpha.wvf_x,alpha.wvf,label = label_alp)
            axs[0].plot(laser.wvf_x[:-limit],conv,label = "Fitted Convolution")
            axs[0].axvline(laser.wvf_x[-limit],color = "grey", ls = ":")
            axs[0].set_ylabel("Normalized Amplitude")  
            axs[0].axhline(0,color = "grey", ls = ":")
            axs[0].set_ylim(1e-4,np.max(alpha.wvf)*1.5)
            axs[0].legend()
            if logy == True:
                axs[0].semilogy()
                axs[1].semilogy()

            axs[1].plot(alpha.wvf_x[np.argmax(alpha.wvf)-np.argmax(func):],func[:np.argmax(func)-np.argmax(alpha.wvf)],label="Convolution Func.")
            axs[1].axhline(0,color = "grey", ls = ":")
            axs[1].set_ylim(1e-6,10)
            axs[1].set_xlabel("Time in [s]"); axs[1].set_ylabel("Convolution signal") 

            plt.show()

            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(p,perr2[0]))
            # output_file.write("%.2E \t\u00B1\t %.2E\n"%(t0,perr1[4]))
            output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[4],perr[4]))
            output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[2],perr[2]))
            output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[0],perr[0]))