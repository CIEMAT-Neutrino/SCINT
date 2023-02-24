import numpy as np
import pandas as pd
import gc #garbage collector interface

def Bin2Np_ADC(FileName,header_lines=6):
    """Dumps ADC binary .dat file with given header lines(6) and wvf size defined in header. \n
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


def save_Bin2Np(file_in,file_out,compressed=True):
    """Self-explainatory. Computation time x10 slower than un-compresed, size x3 times smaller"""
    data_npy=Bin2Np_ADC(file_in)
    if compressed:np.savez_compressed(file_out,data_npy)
    else:         np.save(file_out,data_npy)
    
    del data_npy #free memory
    gc.collect()

def save_Run_Bin2Np(Run,Channel,in_path="../data/raw/",out_path="../data/raw/",out_name="RawADC",Compressed=True) :
    """Run is an int, channel is an int array. In/out paths are strings."""
    for ch in Channel:
        inchan =in_path+"run"+str(Run).zfill(2)+"/wave"+str(ch)+".dat"
        outchan=out_path+"run"+str(Run).zfill(2)+"/"+out_name+"_ch"+str(ch)  
        
        print("-----------------")
        print("Dumping: ",inchan," to: ",outchan+".Np")
        print("-----------------")
        save_Bin2Np(inchan,outchan,compressed=Compressed)

def Bin2Np_excel(excel_file_path="",sheet='Sheet1',compressed=True,i_path="",o_path=""):
    """Calls the dumping function using a excel table with the data runs of our"""
    df = pd.read_excel(excel_file_path, sheet_name=sheet,engine='openpyxl')
    df['Channels']=df['Channels'].apply(lambda x: list(map(int,x.split(",")))) #excell only allows one value per cell, convert channels from string to array of ints

    df.apply(lambda x: save_Run_Bin2Np(x["Run"],x["Channels"],Compressed=compressed,in_path=i_path,out_path=o_path),axis=1,);
