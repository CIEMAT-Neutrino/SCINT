import sys
sys.path.insert(0, '../')
import matplotlib.pyplot as plt

from lib.io_functions  import open_run_var,open_runs_table,do_run_things
from lib.ped_functions import compute_Pedestal
import argparse


# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-r", "--Run", help = "Selected data taking")
parser.add_argument("-e", "--Event", help = "Selected event")
 
# Read arguments from command line
args = parser.parse_args()
 
if args.Run : 
    print("Displaying Run: % s" % args.Run); 
    RUN=int(args.Run)
else        : quit()
if args.Event : 
    print("Displaying Event: % s" % args.Event)
    EV=int(args.Event);
else          : EV=0

RAW=False
compress=False

path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"
Runs=open_runs_table("APSAIA_VUV.xlsx")
RunProps=Runs[Runs["Run"]==RUN].iloc[0]
run_path=path+"run"+str(RunProps["Run"]).zfill(2)+"/";
NEV=open_run_var(run_path,"Timestamp",[RunProps["Channels"][0]],compressed=compress)[RunProps["Channels"][0]].shape[0]

Nchans=len(RunProps["Channels"])
Ncols=int((Nchans+1)/2)
Nrows=int((Nchans)/2)


plt.ion()
if RAW:fig, axs = plt.subplots(dpi=200,ncols= Ncols,nrows=Nrows,figsize=[8,3],sharex=True)
else  :fig, axs = plt.subplots(dpi=200,ncols= Ncols,nrows=Nrows,figsize=[8,3],sharex=True,sharey=True)
while EV<NEV:
    # One channel at a time: 
    z=0;
    for ch in RunProps["Channels"]:
        i=int(z/Ncols)
        j=z%Ncols
        ADC          =open_run_var(run_path,"RawADC"       ,[ch],compressed=True)
        Pedestal_vars=open_run_var(run_path,"Pedestal_vars",[ch],compressed=compress)
        
        ped    = Pedestal_vars[ch]["MEAN"][EV]
        pedSTD = Pedestal_vars[ch]["STD" ][EV]
        axs[i][j].tick_params(axis='both', which='major', labelsize=5)
        axs[i][j].grid()
        if RAW:
            axs[i][j].plot  (  ADC[ch][EV],linewidth=.5 )
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [ped,ped],                   color="tab:red"  ,linewidth=.7)
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [ped+pedSTD,ped+pedSTD],"--",color="tab:red"  ,linewidth=.7)
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [ped-pedSTD,ped-pedSTD],"--",color="tab:red"  ,linewidth=.7)
        else:
            axs[i][j].plot  (  (ADC[ch][EV]-ped)*RunProps["Polarity"][ch],linewidth=.5 )
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [0,0],                   color="tab:red"  ,linewidth=.7)
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [+pedSTD,+pedSTD],"--",color="tab:red"  ,linewidth=.7)
            axs[i][j].plot([0, ADC[ch][EV].shape[0]], [-pedSTD,-pedSTD],"--",color="tab:red"  ,linewidth=.7)

        del Pedestal_vars,ADC
        z+=1;
        
    if Nchans%2==1:axs[-1, -1].axis('off')

    tecla = input("\nPress q to quit, p to save plot, r to go back, n to choose event or any key to continue: ")
    for row in axs: 
        for col in row: col.clear()
    if tecla == "q":
        break
    elif tecla == "r":
        EV -=1
    else:
        EV +=1