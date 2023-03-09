import sys
sys.path.insert(0, '../')
from lib import *

# path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/joython/"
path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"

for run in range(30):
# for run in range(30,50):
# for run in range(1):
    if run==3:continue # Rodrigo forgot one run :D
    Run_props=open_run_properties(run,"APSAIA_VUV.xlsx")
    run_path=path+"run"+str(run).zfill(2)+"/";

    compress=False
    
    
    # One channel at a time: 
    # loading all ch waveforms might demmand too much memory, 
    # remember to always delete between runs to prevent overloading)

    if not Run_props["Type"]=="Visible": continue
    
    for ch in Run_props["Channels"]:
        ADC          =open_run_var(run_path,"RawADC"       ,[ch],compressed=compress)
        Pedestal_vars=open_run_var(run_path,"Pedestal_vars",[ch],compressed=compress)
        Peak_vars    =open_run_var(run_path,"Peak_vars"    ,[ch],compressed=compress)
        
        ADC=do_run_things((ADC,Pedestal_vars,Run_props["Polarity"]),substract_Pedestal)
        Avg_wvf=do_run_things((ADC,Peak_vars),compute_AverageWaveforms)

        save_run_var(Avg_wvf,run_path,"Avg_wvf",compressed=compress)
        
        del Pedestal_vars, ADC

