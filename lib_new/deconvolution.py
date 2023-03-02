import numpy as np
import numba
from numba import njit


#custom function for the filter
def gauss(x, sigma, n, mean = 0, norm = 1):
    a = 1
    if norm == "standard":
        a = 1/(sigma*np.sqrt(2*np.pi))
    else:
        a = norm
    y = a*np.exp(-(x-mean)**n/(2*sigma**n))
    y[0]=0;
    return y

def deconvolve(ADCs:np.ndarray,SER:np.ndarray,FILTER=[])->np.ndarray:
    ADCs_dec=np.zeros(ADCs.shape)
    SER_FFT=np.fft.rfft(SER)
    if  len(FILTER)==0:
        for i in range(ADCs.shape[0]):
            wvf=np.fft.irfft((np.fft.rfft (ADCs[i])/SER_FFT))
            ADCs_dec[i]=wvf
    else:
        for i in range(ADCs.shape[0]):
            wvf=np.fft.irfft((np.fft.rfft (ADCs[i])/SER_FFT)*FILTER)
            ADCs_dec[i]=wvf
    
    return ADCs_dec;
