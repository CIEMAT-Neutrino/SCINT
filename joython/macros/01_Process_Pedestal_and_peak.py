import sys
sys.path.insert(0, '../')

from lib.io_functions  import open_run_var,open_runs_table,open_run_properties,do_run_things,save_run_var
from lib.ped_functions import compute_Pedestal,substract_Pedestal, compute_Peak
# from lib.header import print_header


path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/joython/"
Runs=open_runs_table("../macros/APSAIA_VIS.xlsx")
Runs=Runs[Runs["Run"]==26]


# path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"
# Runs=open_runs_table("../macros/APSAIA_VUV.xlsx")

for run in Runs["Run"].array:

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
        
        Peak_vars=do_run_things(ADC,compute_Peak)
        # save_run_var(ADC,run_path,"ADC",compressed=compress) #no real need to save this, ~1s to load and substract pedestals anyway;
        save_run_var(Pedestal_vars,run_path,"Pedestal_vars",compressed=compress)
        save_run_var(Peak_vars,run_path,"Peak_vars",compressed=compress)
        
        del Pedestal_vars, ADC

