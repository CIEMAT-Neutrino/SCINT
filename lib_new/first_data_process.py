import numpy as np
from itertools import product
import pandas as pd


def binary2npy(FileName,header_lines=6):
    """Dumps root file with given header lines(6) and wvf size defined in header. \n
    Returns a npy array with Raw Wvf 
    If binary files are modified(header/data types), ask your local engineer"""
    
    DEBUG=False
    
    header=np.fromfile(FileName, dtype='I')[:6] #read first event header
    NSamples=int(header[0]/2-header_lines*2)
    Event_size=header_lines*2+NSamples

    data=np.fromfile(FileName, dtype='H');
    N_Events=int( data.shape[0]/Event_size );


    if DEBUG:
        print("Header:",header)
        print("Waveform Samples:",NSamples)
        print("Event_size(wvf+header):",Event_size)
        print("N_Events:",N_Events)
        
    #reshape everything, delete unused header
    data=np.reshape(data,(N_Events,Event_size))[:,header_lines*2:]

    return data;


def bin2npy_compressed(file_in,file_out):
    """Self-explainatory. Computation time x10 slower than un-compresed, size x3 times smaller"""
    data_npy=binary2npy(file_in)
    np.savez_compressed(file_out,data_npy)


def DumpBin2Npz(Run,Channel,in_path="data/raw/",out_path="data/raw/") :
    
    for ch in Channel:
        inchan =in_path+"run"+str(Run).zfill(2)+"/wave"+str(ch)+".dat"
        outchan=out_path+"run"+str(Run).zfill(2)+"/RawADC"+str(ch)  
        
        print("-----------------")
        print("Dumping: ",inchan," to: ",outchan)
        print("-----------------")
        bin2npy_compressed(inchan,outchan)

def Bin2Npz_excel(excel_file_path=""):

    df = pd.read_excel(excel_file_path, sheet_name='Sheet1')
    df['Channel']=df['Channel'].apply(lambda x: list(map(int,x.split(",")))) #excell only allows one value per cell, convert string to array of channels

    # branches = ["RawADC", "NBinsWvf", "Sampling", "Label", "RawPChannel"]
    df.apply(lambda x: DumpBin2Npz(x["Run"],x["Channel"]),axis=1);
