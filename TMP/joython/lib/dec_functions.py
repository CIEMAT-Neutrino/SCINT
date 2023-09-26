import numpy as np
import numexpr as ne
##For now, numba doesn't support np.fft, stay tunned for this: https://github.com/numba/numba/issues/5864

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
    ped=250;
    SER_FFT=np.fft.rfft(SER)
    if  len(FILTER)==0:
        for i in range(ADCs.shape[0]):
            wvf=np.fft.irfft((np.fft.rfft (ADCs[i])/SER_FFT))
            ADCs_dec[i]=wvf
    else:
        for i in range(ADCs.shape[0]):
            wvf=np.fft.irfft((np.fft.rfft (ADCs[i])/SER_FFT)*FILTER)
            ADCs_dec[i]=wvf

    #substract pedestal again
    a=ADCs_dec.T
    b=np.mean(ADCs_dec[:,:ped],axis=1).T
    ADCs_dec=ne.evaluate( '(a-b)').T #optimizing, multithreading

    return ADCs_dec;

#Framework interface, not debugged yet
def compute_DecWvf(VARS:tuple)->np.ndarray:
    if len(VARS)==2:#no filter involved
        adc,ser=VARS
        return deconvolve(adc,ser)
    elif len(VARS)==3:#with filter
        adc,ser,filt=VARS
        return deconvolve(adc,ser,filt)
    else:
        raise NotImplementedError("Inputs must be 2 or 3 tuple longs")