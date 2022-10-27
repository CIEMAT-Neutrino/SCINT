import numpy as np
from curve import Curve
import matplotlib.pyplot as plt
from .io_functions import load_analysis_npy
from .io_functions import check_key
from .wvf_functions import smooth
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

def deconvolve(my_runs,CLEAN,OPT,PATH = "../data/dec/"):
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
            # Select required runs and parameters
            if AVE == "ADC": 
                PED = ana_runs[run][ch]["Ped_mean"][i]    
                POL = ana_runs[run][ch]["P_channel"]
                RAW = POL*(my_runs [run][ch]["ADC"][i]-PED)

            else: 
                RAW = my_runs[run][ch][AVE]

            # Can be used for test to trimm array
            if check_key(OPT, "TRIMM") == True: TRIMM = OPT["TRIMM"]
            if check_key(OPT, "AUTO_TRIMM") == True:
                j = 0
                while 2**j < len(RAW):
                    j = j+1

                TRIMM = len(RAW)-2**(j-1)

            if TRIMM != 0: 
                SIGNAL = RAW[:-TRIMM]
                KERNEL = CLEAN[:-TRIMM]
                print("Array length after trimming = %i"%len(SIGNAL))
            
            else: SIGNAL = RAW
            
            if check_key(OPT, "SMOOTH") == True:
                if OPT["SMOOTH"] > 0:
                    SIGNAL = smooth(SIGNAL,OPT["SMOOTH"])
                else:
                    print("Invalid value encountered in smooth")

            STD = ana_runs[run][ch]["Ped_STD"][i]
            X = 4e-9*np.arange(len(SIGNAL))
            
            # Define noise (should be imported in future iterations)
            NOISE = STD*np.random.randn(len(SIGNAL))
            FFT_NOISE = np.fft.rfft(NOISE)

            # Roll signal to align wvfs
            while np.argmax(SIGNAL) < np.argmax(KERNEL):
                SIGNAL = np.roll(SIGNAL,1)    
            
            # Calculate FFT arrays
            FFT_SIGNAL = np.fft.rfft(SIGNAL)
            FFT_SIGNAL_X = np.fft.rfftfreq(len(SIGNAL),4e-9)
            FFT_KERNEL = np.fft.rfft(KERNEL)
            FFT_KERNEL_X = np.fft.rfftfreq(len(KERNEL),4e-9)
            WIENER = abs(FFT_KERNEL)**2/(abs(FFT_KERNEL)**2+abs(FFT_NOISE)**2)
            
            # Interpolate wiener envelop for fit of gaussian filter
            WIENER_BUFFER = 800
            WIENER_CURVE = Curve(FFT_KERNEL_X[:-WIENER_BUFFER],(-1*WIENER[:-WIENER_BUFFER])+2)
            ENV = WIENER_CURVE.envelope2(tc=1e6)
            ENV_WIENER = scipy.interpolate.interp1d(ENV.x, ENV.y)
            ENV_WIENER_Y = ENV_WIENER(FFT_SIGNAL_X[:-WIENER_BUFFER])
            ENV_WIENER_MIN = np.argmin(-1*(ENV_WIENER_Y-2))

            # Select fit parameters and perform fit to determin cut-off
            p0 = [100,1.999999]
            lim = [[10,1],[2000,8]]
            if check_key(OPT,"FIX_EXP") == True and OPT["FIX_EXP"] == True:
                lim = [[10,1.99999],[2000,2]]
            
            try:
                params,cov=curve_fit(fit_gauss, np.arange(len(FFT_SIGNAL_X))[:ENV_WIENER_MIN], np.log10(-1*(ENV_WIENER_Y[:ENV_WIENER_MIN]-2)),p0=p0,bounds=lim)
            except:
                params = p0
                print("FIT COULD NOT BE PERFORMED!")
            print("Filter strengh %f and exp %f"%(params[0],params[1]))
            
            # Generate gauss filter and filtered signal
            FFT_GAUSS = gauss(np.arange(len(FFT_SIGNAL)),*params)
            FFT_GAUSS_SIGNAL = FFT_SIGNAL*FFT_GAUSS
            GAUSS_SIGNAL = np.fft.irfft(FFT_GAUSS_SIGNAL)
            
            # Generate deconvoluted function
            FFT_DEC = FFT_GAUSS_SIGNAL/np.array(FFT_KERNEL/np.max(FFT_KERNEL))
            DEC = np.fft.irfft(FFT_DEC)
            if check_key(OPT, "REVERSE") == True and OPT["REVERSE"] == True: DEC = DEC[::-1]
            DEC = np.roll(DEC,np.argmax(KERNEL)) # Roll the function to match original position
            
            #-------------------------------------------------------------------------------------------------------------------
            # Plot results: left shows process in time space; right in frequency space.
            #-------------------------------------------------------------------------------------------------------------------
            
            plt.ion()
            next_plot = False
            plt.rcParams['figure.figsize'] = [16, 8]
            plt.subplot(1,2,1)
            plt.plot(X,SIGNAL,label = "SIGNAL: int = %.4E" %(np.trapz(SIGNAL,X)),c="tab:blue")
            plt.plot(X,GAUSS_SIGNAL, label = "GAUSS_SIGNAL: int = %.4E" %(np.trapz(GAUSS_SIGNAL,X)),c="blue")
            plt.plot(X,DEC,label = "DECONVOLUTION: int = %.4E" %(np.trapz(DEC,X)),c="tab:green")
            plt.ylabel("ADC Counts");plt.xlabel("Time in [s]")
            if check_key(OPT,"LOGY") == True and OPT["LOGY"] == True: plt.semilogy()
            if check_key(OPT,"FOCUS") == True and OPT["LOGY"] == True: 
                plt.xlim(4e-9*np.array([np.argmax(SIGNAL)-100,np.argmax(SIGNAL)+1000]))
                plt.ylim([np.min(SIGNAL)*1.1,np.max(DEC)*1.1])
            plt.legend()
            
            plt.subplot(1,2,2)
            if check_key(OPT,"SHOW_F_SIGNAL") != False: plt.plot(FFT_SIGNAL_X,np.abs(FFT_SIGNAL),label = "SIGNAL",c="tab:blue")
            if check_key(OPT,"SHOW_F_GSIGNAL") != False: plt.plot(FFT_SIGNAL_X,np.abs(GAUSS_SIGNAL),label = "GAUSS_SIGNAL",c="blue")
            if check_key(OPT,"SHOW_F_DET_RESPONSE") != False: plt.plot(FFT_KERNEL_X,np.abs(FFT_KERNEL),label = "DET_RESPONSE",c="tab:orange")
            
            if check_key(OPT,"SHOW_F_DEC") != False: plt.plot(FFT_SIGNAL_X,np.abs(FFT_DEC),label = "DECONVOLUTION",c="tab:green")
            if check_key(OPT,"SHOW_F_WIENER") != False: 
                plt.plot(FFT_SIGNAL_X,WIENER,label = "WIENER",c="tab:red")
                plt.plot(ENV_WIENER.x[:ENV_WIENER_MIN],-1*(ENV_WIENER.y[:ENV_WIENER_MIN]-2),label = "ENV_WIENER",c="tab:pink",ls="--")

            if check_key(OPT,"SHOW_F_GAUSS") != False: plt.plot(FFT_SIGNAL_X,FFT_GAUSS,label = "GAUSS",c="k",ls="--")
            plt.ylabel("a.u.");plt.xlabel("Frequency in [Hz]")
            plt.ylim(1e-8,np.max(FFT_KERNEL)*10)
            plt.semilogy();plt.semilogx()
            plt.legend()

            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()