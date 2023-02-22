import sys
sys.path.insert(0, '../')

from lib_new.io_lib  import open_run_var,open_run_properties,do_run_things,save_run_var
from lib_new.ped_lib import compute_Pedestal,substract_Pedestal
from lib.header import print_header
import gc #garbage collector interface


# for run in [1,2,3,9,10,11,25,26,27]:
for run in [2]:
    path="../data/raw/run"+str(run).zfill(2)+"/";
    Run_props=open_run_properties(run,"Runs_list.xlsx")

    compress=False
    
    
    # One channel at a time: 
    # loading all ch waveforms might demmand too much memory, 
    # remember to always delete between runs to prevent overloading)

    for ch in Run_props["Channels"]:
        ADC=open_run_var(path,"RawADC",[ch],compressed=compress)
        
        Pedestal_vars=do_run_things(ADC,compute_Pedestal)
        ADC=do_run_things((ADC,Pedestal_vars,Run_props["Polarity"]),substract_Pedestal)
        
        # save_run_var(ADC,path,"ADC",compressed=compress) #no real need to save this, ~1s to load and substract pedestals anyway;
        save_run_var(Pedestal_vars,path,"Pedestal_vars")
        
        del Pedestal_vars, ADC

