import numpy as np
from curve import Curve
import matplotlib.pyplot as plt

from .io_functions import check_key
from .wvf_functions import smooth,find_baseline_cuts

import scipy.interpolate
from scipy.optimize import curve_fit
from itertools import product

def gauss(X,STD,N,MEAN=0,NORM=1):
    A=1
    if NORM=="standard":
        A=1/(STD*np.sqrt(2*np.pi))
    else:
        A=NORM
    Y=A*np.exp(-(X-MEAN)**N/(2*STD**N))
    return Y

def fit_gauss(X,STD,N,MEAN=0,NORM=1):
    A=1
    if NORM=="standard":
        A=1/(STD*np.sqrt(2*np.pi))
    else:
        A=NORM
    Y=A*np.exp(-(X-MEAN)**N/(2*STD**N))
    return np.log10(Y)

def deconvolve(my_runs,out_runs,dec_runs,OPT={}):
    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        aux = dict()
        TRIMM = 0
        if check_key(OPT,"KEY") == True: KEY = OPT["KEY"]
        else: 
            KEY = "Ana_ADC"
            print("Selected default wvf key %s"%KEY)
        
        CLEAN = dec_runs[run][ch]["ADC"][0]
        for i in range(len(my_runs[run][ch][KEY])):
            # Select required runs and parameters

            RAW = my_runs[run][ch][KEY][i]
            
            # Roll signal to align wvfs
            rollcount = 0
            while np.argmax(RAW) < np.argmax(CLEAN):
                RAW = np.roll(RAW,1)    
                rollcount = rollcount + 1

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

        dec_key = "Dec_"+KEY
        out_runs[run][ch][dec_key] = aux
        print("Generated wvfs with key %s"%dec_key)
    return aux,X