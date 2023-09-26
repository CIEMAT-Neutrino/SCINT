# ---------------------------------------------------------------------------------------------------------------------- #                                                     #
#  ============================================ RUN:$ python3 STD_check.py "path/file1" ================================ #
# This macro will process the RAW DATA to get monitoring plots for the setup noise parameters                            #
# This macro is independent of the CYTHON_TOOLS library and can be used without having cloned the repository.            #
# You just need to be sure of having the packages installed in your computer.                                            #
# FROM PCAE177 RUN ---->  source /data/WaveDumpData/SBND_XA_PDE/CYTHON_TOOLS/joython/my_env/bin/activate                 #
# ---------------------------------------------------------------------------------------------------------------------- #

#############
## IMPORTS ##
#############
import sys, numba
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import numexpr as ne

###############
## FUNCTIONS ##
###############
def binary2npy_express(in_file, header_lines=6, debug=False):
    '''
    Dumps ADC binary .dat file with given header lines(6) and wvf size defined in header. \n
    Returns a npy array with Raw Wvf 
    If binary files are modified(header/data types), ask your local engineer
    '''
    
    headers = np.fromfile(in_file, dtype='I') # Reading .dat file as uint32 (First event header)
    header  = headers[:6]                      # Read first event header
    
    NSamples   = int(header[0]/2-header_lines*2)   # Number of samples per event (as uint16)
    Event_size = header_lines*2+NSamples           # Number of uint16 per event
    data       = np.fromfile(in_file, dtype='H'); # Reading .dat file as uint16
    N_Events   = int( data.shape[0]/Event_size );  # Number of events in the file

    data    = np.reshape(data,(N_Events,Event_size))[:,header_lines*2:]
    headers = np.reshape(headers,(N_Events , int(Event_size/2) )  )[:,:header_lines]
    headers = headers.astype(float)
   
    TIMESTAMP  = (headers[:,4]*2**32 + headers[:,5]) * 8e-9 # Unidades TriggerTimeStamp(PC_Units) * 8e-9

    if debug:
        print("\n#####################################################################")
        print("Header:",header)
        print("Waveform Samples:",NSamples)
        print("Event_size(wvf+header):",Event_size)
        
        print("N_Events:",N_Events)
        print("Run time: {:.2f}".format((TIMESTAMP[-1]-TIMESTAMP[0])/60) + " min" )
        print("Rate: {:.2f}".format(N_Events/(TIMESTAMP[-1]-TIMESTAMP[0])) + " Events/s" )
        print("#####################################################################\n")

    return data, TIMESTAMP;

def compute_Pedestal(ADC,ped_lim=50):
    pedestal_vars = dict();
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
    if   num > 0: return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0: return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:         return arr #no shift

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

def custom_legend_name(fig_px,new_names):
    for i, new_name in enumerate(new_names): fig_px.data[i].name = new_name
    return fig_px

def custom_plotly_layout(fig_px, xaxis_title="", yaxis_title="", title="",barmode="stack"):
    fig_px.update_layout( updatemenus=[ dict( buttons=list([ dict(args=[{"xaxis.type": "linear", "yaxis.type": "linear"}], label="LinearXY", method="relayout"),
                                                             dict(args=[{"xaxis.type": "log", "yaxis.type": "log"}],       label="LogXY",    method="relayout"),
                                                             dict(args=[{"xaxis.type": "linear", "yaxis.type": "log"}],    label="LogY",     method="relayout"),
                                                             dict( args=[{"xaxis.type": "log", "yaxis.type": "linear"}],   label="LogX",     method="relayout") ]),
                          direction="down", pad={"r": 10, "t": 10}, showactive=True, x=-0.1, xanchor="left", y=1.5, yanchor="top" ) ] )
    fig_px.update_layout(   template="presentation", title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title, barmode=barmode,
                            font=dict(family="serif"), legend_title_text='', legend = dict(yanchor="top", xanchor="right", x = 0.99), showlegend=True)
    fig_px.update_xaxes(showline=True,mirror=True,zeroline=False)
    fig_px.update_yaxes(showline=True,mirror=True,zeroline=False)
    return fig_px

###############
## ARGUMENTS ##
###############
try:               input_files = sys.argv[1]
except IndexError: input_files = input("Please introduce the input \"PATH/File\" you want to analyse (separated with commas): ")
file_list = [str(f) for f in input_files.split(",")]

##########
## MAIN ##
##########
adcs_list = []; timestamp_list = []; peds_vars_list = []
for f in file_list:
    print("\nINPUT FILE: ", f)
    ADCs, TIMESTAMP = binary2npy_express(f,header_lines=6);
    ADCs = ADCs.astype(float) # Convert to float, numba meses up with int16
    print("Number of waveforms:", ADCs.shape[0])
    print("Waveform size:"      , ADCs.shape[1])

    print("Computing Pedestal Variables...")
    ped_vars = compute_Pedestal_slidingWindows(ADCs,ped_lim=400,sliding=50,pretrigger=800)
    ADCs = substract_Pedestal([ADCs,ped_vars,1])

    print("\nDONE !!\n")
    print("STD:" ,np.std (ped_vars["STD"]))
    print("MEAN:",np.mean(ped_vars["STD"]))

    adcs_list.append(ADCs); timestamp_list.append(TIMESTAMP)
    peds_vars_list.append(ped_vars)

#PLOT
data2plot = []; label2plot = [];
for pdx, p in enumerate(peds_vars_list): data2plot.append(p["STD"]); label2plot.append(file_list[pdx].split("/")[-1])

fig_px = px.histogram(x=data2plot, opacity=1/len(file_list))
custom_legend_name(fig_px, label2plot)
custom_plotly_layout(fig_px, xaxis_title="Pedestal STD [ADCs]", yaxis_title="Counts", title="Pedestal STD histogram",barmode="overlay")
fig_px.show()

#AMPLITUDE
data2plot = []; label2plot = [];
for adx, a in enumerate(adcs_list): data2plot.append(np.max(a, axis=1)); label2plot.append(file_list[adx].split("/")[-1])
fig_px = px.histogram(x=data2plot, opacity=1/len(file_list))
custom_legend_name(fig_px, label2plot)
custom_plotly_layout(fig_px, xaxis_title="PeakAmp [ADCs]", yaxis_title="Counts", title="PeakAmp histogram",barmode="overlay")
fig_px.show()

# old_way
# source /data/WaveDumpData/SBND_XA_PDE/CYTHON_TOOLS/joython/my_env/bin/activate
# python3 /data/WaveDumpData/SBND_XA_PDE/CYTHON_TOOLS/joython/STD_check.py -f /data/WaveDumpData/SBND_XA_PDE/DAPHNE_VUV/run00/wave5.dat
