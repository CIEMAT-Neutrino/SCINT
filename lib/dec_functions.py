import numpy as np
from curve import Curve
import matplotlib.pyplot as plt
from .io_functions import load_analysis_npy
from .io_functions import check_key
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

def deconvolve(my_runs,KERNEL,FS,TRIMM,OPT,PATH = "../data/dec/"):
    try:
        ana_runs = load_analysis_npy(my_runs["N_runs"],my_runs["N_channels"])
    except:
        print("Events have not been processed")
    if TRIMM != 0: KERNEL = KERNEL[:-TRIMM]

    for run,ch in product(my_runs["N_runs"],my_runs["N_channels"]):
        for i in range(len(my_runs[run][ch]["ADC"])):
            RAW = my_runs [run][ch]["ADC"][i]
            PED = ana_runs[run][ch]["Ped_mean"][i]    
            STD = ana_runs[run][ch]["Ped_STD"][i]
            POL = ana_runs[run][ch]["P_channel"]
            
            if TRIMM != 0: SIGNAL = POL*(RAW[:-TRIMM]-PED)
            else: SIGNAL = POL*(RAW-PED)
            
            NOISE = 20*np.random.randn(len(SIGNAL))
            FFT_NOISE = np.fft.rfft(NOISE)

            while np.argmax(SIGNAL) < np.argmax(KERNEL):
                SIGNAL = np.roll(SIGNAL,1)    
            
            FFT_SIGNAL = np.fft.rfft(SIGNAL)
            FFT_SIGNAL_X = np.fft.rfftfreq(len(SIGNAL),4e-9)
            FFT_KERNEL = np.fft.rfft(KERNEL)
            FFT_KERNEL_X = np.fft.rfftfreq(len(KERNEL),4e-9)
            WIENER = abs(FFT_KERNEL)**2/(abs(FFT_KERNEL)**2+abs(FFT_NOISE)**2)
            
            WIENER_CURVE = Curve(FFT_KERNEL_X,(-1*WIENER)+2)
            # print(len(FFT_KERNEL_X))
            ENV = WIENER_CURVE.envelope2(tc=1e6)
            # print(len(ENV_WIENER.x))

            ENV_WIENER = scipy.interpolate.interp1d(ENV.x, ENV.y)
            ENV_WIENER_Y = ENV_WIENER(FFT_SIGNAL_X)
            p0 = [100,2]
            # lim = [[10,1],[1000,10]]
            
            ENV_WIENER_MIN = np.argmin(-1*(ENV_WIENER_Y-2))
            # print(ENV_WIENER_MIN)

            params,cov=curve_fit(fit_gauss, np.arange(len(FFT_SIGNAL_X))[:ENV_WIENER_MIN], np.log10(-1*(ENV_WIENER_Y[:ENV_WIENER_MIN]-2)),p0=p0)
            
            # plt.plot(FFT_SIGNAL_X[:ENV_WIENER_MIN],-1*(ENV_WIENER_Y[:ENV_WIENER_MIN]-2))
            # plt.plot(FFT_SIGNAL_X[:ENV_WIENER_MIN],gauss(np.arange(len(FFT_SIGNAL)),*params)[:ENV_WIENER_MIN],label = "GAUSS",c="k")
            # plt.semilogx();plt.semilogy()
            # plt.show()

            # FFT_GAUSS = gauss(np.arange(len(FFT_SIGNAL)),FS,2)
            FFT_GAUSS = gauss(np.arange(len(FFT_SIGNAL)),*params)
            # print(*params)
            GAUSS_SIGNAL = FFT_SIGNAL*FFT_GAUSS
            
            FFT_DEC = GAUSS_SIGNAL/np.array(FFT_KERNEL/np.max(FFT_KERNEL))
            DEC = np.fft.irfft(FFT_DEC)
            DEC = np.roll(DEC,np.argmax(KERNEL))
            
            plt.ion()
            next_plot = False
            plt.rcParams['figure.figsize'] = [16, 8]
            plt.subplot(1,2,1)
            plt.plot(np.arange(len(SIGNAL))*4e-9,SIGNAL,label = "SIGNAL",c="tab:blue")
            # plt.plot(np.arange(len(KERNEL))*4e-9,KERNEL,label = "KERNEL")
            plt.plot(np.arange(len(np.fft.irfft(GAUSS_SIGNAL)))*4e-9,np.fft.irfft(GAUSS_SIGNAL), label = "GAUSS_SIGNAL",c="blue")
            plt.plot(np.arange(len(DEC))*4e-9,DEC,label="DECONVOLUTION",c="tab:green")
            plt.ylabel("ADC Counts");plt.xlabel("Time in [s]")
            if check_key(OPT,"LOGY") == True: plt.semilogy()
            if check_key(OPT,"FOCUS") == True: 
                plt.xlim(4e-9*np.array([np.argmax(SIGNAL)-100,np.argmax(SIGNAL)+1000]))
                plt.ylim([-10,np.max(DEC)*1.1])
            plt.legend()
            
            plt.subplot(1,2,2)
            plt.plot(FFT_SIGNAL_X,np.abs(FFT_SIGNAL),label = "SIGNAL",c="tab:blue")
            plt.plot(FFT_SIGNAL_X,np.abs(GAUSS_SIGNAL),label = "GAUSS_SIGNAL",c="blue")
            plt.plot(FFT_KERNEL_X,np.abs(FFT_KERNEL),label = "DET_RESPONSE",c="tab:orange")
            
            plt.plot(FFT_SIGNAL_X,np.abs(FFT_DEC),label = "DECONVOLUTION",c="tab:green")
            plt.plot(FFT_SIGNAL_X,WIENER,label = "WIENER",c="tab:red")
            plt.plot(ENV_WIENER.x[:ENV_WIENER_MIN],-1*(ENV_WIENER.y[:ENV_WIENER_MIN]-2),label = "ENV_WIENER",c="tab:pink")

            plt.plot(FFT_SIGNAL_X,FFT_GAUSS,label = "GAUSS",c="k")
            # ENV_WIENER.plot(label="ENV_WIENER")
            plt.ylabel("a.u.");plt.xlabel("Frequency in [Hz]")
            plt.ylim(1e-6,np.max(FFT_KERNEL)*10)
            plt.semilogy();plt.semilogx()
            plt.legend()
            
            while not plt.waitforbuttonpress(-1): pass

            plt.clf()

        plt.ioff()