import matplotlib.pyplot as plt
import numpy as np
import uproot

from pynput import keyboard

# def on_press(key):
#     try:
#         print('alphanumeric key {0} pressed'.format(
#             key.char))
#     except AttributeError:
#         print('special key {0} pressed'.format(
#             key)) 

def root2npy (in_path,out_path):
    DEBUG=False;
    """Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. \n Depends on uproot, awkward and numpy. \n Size increases x2 times. """
    # in_path ="../data/run26_ch6.root"
    # out_path="../data/run26_ch6.npy"
    f=uproot.open(in_path)
    my_dict={}
    print("----------------------")
    print("Dumping file:", in_path)
    for branch in f["IR02"].keys():
        if DEBUG: print("dumping brach:",branch)
        my_dict[branch]=f["IR02"][branch].array().to_numpy()
    my_dict["NBins_wvf"]=my_dict["ADC"][0].shape[0]
    print(my_dict.keys())

    np.save(out_path,my_dict)
    print("Saved data in:" , out_path)

def load_npy(RUNS,CH,POL,PATH = "../data/"):
    """Structure: run_dict[RUN][CH][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels"""

    # RUNS=[
    #     # "02",
    #     "10",
    #     "22",
    #     # "26"
    #     ]
    # CH=[0,1,4,6]

    runs=dict();
    runs["N_runs"]    =RUNS;
    runs["N_channels"]=CH;
    runs["P_channels"]=POL;
    
    for run in RUNS:
        channels=dict();
        for ch in CH:
            channels[ch]=np.load(PATH+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy",allow_pickle=True).item()
        runs[run]=channels
    return runs

def compute_pedestal_variables(my_runs,nbins):
    """Computes the pedestal variables of a collection of a run's collection in standard format"""

    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Ped_STD"] =np.std (my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_mean"]=np.mean(my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_max"] =np.max (my_runs[run][ch]["ADC"][:,:nbins],axis=1)
            my_runs[run][ch]["Ped_min"] =np.min (my_runs[run][ch]["ADC"][:,:nbins],axis=1)

def compute_peak_variables(my_runs,range1=0,range2=0):
    """Computes the peaktime and amplitude of a collection of a run's collection in standard format"""
    # to do: implement ranges 
    for run in my_runs["N_runs"]:
        for ch in my_runs["N_channels"]:
            my_runs[run][ch]["Peak_amp" ] =np.max    (my_runs[run][ch]["ADC"][:,:]*my_runs["P_channels"][ch],axis=1)
            my_runs[run][ch]["Peak_time"] =np.argmax (my_runs[run][ch]["ADC"][:,:]*my_runs["P_channels"][ch],axis=1)

def vis_raw_npy(RUN,CH,PATH = ""):
    buffer = 20
    runs=dict()
    channels=dict()
    channels[CH]=np.load("data/run"+RUN+"_ch"+str(CH)+".npy",allow_pickle=True).item()
    runs[RUN]=channels
    
    plt.ion()
    next_plot = False


    for i in range(len(runs[RUN][CH]["ADC"])):
        min = np.argmin(runs[RUN][CH]["ADC"][i])
        try:
            PED = runs[RUN][CH]["Ped_mean"][i]    
            STD = runs[RUN][CH]["Ped_STD"][i]    
        except:
            PED = np.mean(runs[RUN][CH]["ADC"][i][:min-buffer])
            STD = np.std(runs[RUN][CH]["ADC"][i][:min-buffer])
            plt.title("PED and Signal time evaluated at vis. time")
        
        plt.xlabel("Time in [s]")
        plt.ylabel("ADC Counts")
        plt.plot(np.arange(len(runs[RUN][CH]["ADC"][i]))*4e-9,np.array(runs[RUN][CH]["ADC"][i]))
        
        try:
            # plt.axhline(len(runs[RUN][CH]["Pedestal"]),c="red")
            plt.plot(4e-9*np.array([min-buffer,min-buffer]),[PED+5*STD,PED-5*STD],c="green")
            plt.axhline(PED,c="red")
            plt.axhline(PED+STD,c="k",alpha=0.5,ls="--")
            plt.axhline(PED-STD,c="k",alpha=0.5,ls="--")
        except:
            print("Unprocessed WVFs. Run Processing.py to obtain pedestal information.")
        
        while not plt.waitforbuttonpress(-1): pass

        # listener = keyboard.Listener(on_press=on_press)
        # listener.start()

        plt.clf()

    plt.ioff()
