import numpy as np
import matplotlib.pyplot as plt
import numba
import argparse
import numexpr as ne

#FUNCTIONS
def Bin2Np_ADC(FileName,header_lines=6):
    """Dumps ADC binary .dat file with given header lines(6) and wvf size defined in header. \n
    Returns a npy array with Raw Wvf 
    If binary files are modified(header/data types), ask your local engineer"""
    
    DEBUG=False
    
    headers= np.fromfile(FileName, dtype='I') #read first event header
    header = headers[:6] #read first event header
    NSamples=int(header[0]/2-header_lines*2)
    Event_size=header_lines*2+NSamples

    data=np.fromfile(FileName, dtype='H');
    N_Events=int( data.shape[0]/Event_size );

    data    = np.reshape(data,(N_Events,Event_size))[:,header_lines*2:]
    headers = np.reshape(headers,(N_Events , int(Event_size/2) )  )[:,:header_lines]
    headers=headers.astype(float)
    
    first=headers[:,4]*2**32
    second=headers[:,5]
    TIMESTAMP  = first + second 
    TIMESTAMP *= 8e-9 #Unidades TriggerTimeStamp(PC_Units) * 8e-9

    if DEBUG:
        print("Header:",header)
        print("Waveform Samples:",NSamples)
        print("Event_size(wvf+header):",Event_size)
        
        print("N_Events:",N_Events)
        print("Run time: {:.2f}".format((TIMESTAMP[-1]-TIMESTAMP[0])/60) + " min" )
        print("Rate: {:.2f}".format(N_Events/(TIMESTAMP[-1]-TIMESTAMP[0])) + " Events/s" )
        print("#####################################################################\n")

    return data , TIMESTAMP;

def compute_Pedestal(ADC,ped_lim=50):
    pedestal_vars=dict();
    pedestal_vars["STD"]   = np.std (ADC[:,:ped_lim],axis=1)
    pedestal_vars["MEAN"]  = np.mean(ADC[:,:ped_lim],axis=1)
    pedestal_vars["MAX"]   = np.max (ADC[:,:ped_lim],axis=1)
    pedestal_vars["Min"]   = np.min (ADC[:,:ped_lim],axis=1)
    return pedestal_vars;

@numba.njit
def shift_ADCs(ADC,shift):
        N_wvfs=ADC.shape[0]
        aux_ADC=np.zeros(ADC.shape)
        for i in range(N_wvfs):
            aux_ADC[i]=shift4_numba(ADC[i],int(shift[i])) # Shift the wvfs
        return aux_ADC;

@numba.njit
def shift4_numba(arr, num, fill_value=0):#default shifted value is 0, remember to always substract your pedestal first
    if   num > 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:#no shift
        return arr

def compute_Pedestal_slidingWindows(ADC,ped_lim=400,sliding=50,pretrigger=800):
    """Taking the best between different windows in pretrigger"""
    slides=int((pretrigger-ped_lim)/sliding);
    N_wvfs=ADC.shape[0];
    aux=np.zeros((N_wvfs,slides))
    for i in range(slides):
        aux[:,i]=np.std (ADC[:,(i*sliding):(i*sliding+ped_lim)],axis=1)

    #put first in the wvf the appropiate window, the one with less std:
    shifts= np.argmin (aux,axis=1)
    shifts*=(-1)*sliding;#weird segmentation fault if used in line b4;
    ADC_s = shift_ADCs(ADC,shifts)

    #compute all ped variables, now with the best window available
    slided_ped_vars=compute_Pedestal(ADC_s,ped_lim)
    return slided_ped_vars;

def substract_Pedestal(Vars,pol=1):
    ADC_raw, pedestal , polarity= Vars
    
    
    a=ADC_raw.T
    b=pedestal["MEAN"].T
    
    ADC_raw=ne.evaluate( '(a-b)*polarity').T #optimizing, multithreading
    return ADC_raw;

## ARGUMENTS
# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-f", "--File", help = "File_Path")
 
# Read arguments from command line
args = parser.parse_args()
 
if args.File : 
    print("Reading file: % s" % args.File); 
    File=str(args.File)
else:
    raise ValueError("No file given");

#MAIN
ADCs, TIMESTAMP = Bin2Np_ADC(File,header_lines=6);
ADCs=ADCs.astype(float) #convert to float, numba meses up with int16
print("Number of waveforms:",ADCs.shape[0])
print("Waveform size:"      ,ADCs.shape[1])

print("Computing Pedestal Variables...")
ped_vars=compute_Pedestal_slidingWindows(ADCs,ped_lim=400,sliding=50,pretrigger=800)

print("Done...")
print("std:" ,np.std (ped_vars["STD"]))
print("mean:",np.mean(ped_vars["STD"]))

#PLOT
plt.figure(dpi=200);
plt.hist(ped_vars["STD"],500,[0,10]);
plt.yscale("log");
plt.grid();
plt.show();

#AMPLITUDE
ADCs=substract_Pedestal([ADCs,ped_vars,1])
plt.figure(dpi=200);
plt.hist(np.max(ADCs,axis=1),500,[0,5000]);
plt.yscale("log");
plt.grid();
plt.show();
