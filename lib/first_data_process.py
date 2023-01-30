import numpy as np
from itertools import product



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

def bin2npy(file_in,file_out):
    """Self-explainatory. Computation time x10 faster than compresed, size x3 times bigger"""
    data_npy=binary2npy(file_in)
    np.save(file_out,data_npy)

    #GZip: too time expensive slightly smaller (1/2%) than numpy savez
    # import gzip
    # f = gzip.GzipFile("run131/wave6.npy.gz", "w")
    # np.save(file=f, arr=data_npy)
    # f.close()

def bin2npy_compressed(file_in,file_out):
    """Self-explainatory. Computation time x10 slower than un-compresed, size x3 times smaller"""
    data_npy=binary2npy(file_in)
    np.savez_compressed(file_out,data_npy)


def DumpBin2npy(runs, channels, in_path="../data/raw/", out_path="../data/raw/", info={},compressed=True, debug=False):
    """
    Dumper from binary format to npy tuples. 
    Input are binary input file path and npy outputfile as strings. 
    \n Depends numpy. 
    """

    for run, ch in product (runs.astype(int),channels.astype(int)):
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file  = "run"+str(run).zfill(2)+"/wave"+str(ch)+".dat"
        out_file = "run"+str(run).zfill(2)+"_ch"+str(ch)+".npz"
        if not compressed:
            out_file = "run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
        
        try:
            my_dict = {}
            
            if debug:
                print("----------------------")
                print("Dumping file:", in_path+in_file)
            
            ADC = binary2npy(in_path+in_file)
            my_dict["ADC"]=ADC
            
            # additional useful info
            my_dict["NBinsWvf"] = my_dict["ADC"][0].shape[0]
            my_dict["Sampling"] = info["SAMPLING"][0]
            my_dict["Label"] = info["CHAN_LABEL"][j]
            my_dict["PChannel"] = int(info["CHAN_POLAR"][j])

            if compressed:
                np.savez_compressed(out_path+out_file,my_dict)
            else:
                np.save(out_path+out_file,my_dict)

            if debug:
                print(my_dict.keys())
                print("Saved data in:" , out_path+out_file)
                print("----------------------\n")

        except FileNotFoundError:
            print("--- File %s was not foud!!! \n"%in_file)
