import sys
sys.path.insert(0, '../')
from lib import *



path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/joython/"
Runs=open_runs_table("../macros/APSAIA_VIS.xlsx")

# path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"
# Runs=open_runs_table("../macros/APSAIA_VUV.xlsx")
# Runs=Runs[Runs["Run"]==39]

for run in Runs["Run"].array:
    if run==3:continue # Rodrigo forgot one run :D
    Run_props=open_run_properties(run,"APSAIA_VUV.xlsx")
    run_path=path+"run"+str(run).zfill(2)+"/";

    compress=False
    
    
    # One channel at a time: 
    # loading all ch waveforms might demmand too much memory, 
    # remember to always delete between runs to prevent overloading)

    for ch in Run_props["Channels"]:
        ADC=open_run_var(run_path,"RawADC",[ch],compressed=compress)
        
        Pedestal_vars=do_run_things(ADC,compute_Pedestal)
        ADC=do_run_things((ADC,Pedestal_vars,Run_props["Polarity"]),substract_Pedestal)
        
        Charge_vars=do_run_things(ADC,compute_ChargeRange)
        save_run_var(Charge_vars,run_path,"Charge_vars",compressed=compress)
        
        del Pedestal_vars, ADC

