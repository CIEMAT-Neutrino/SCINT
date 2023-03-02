from lib import *

for run in [1,2,3,9,10,11,25,26,27]:
    path="../data/raw/run"+str(run).zfill(2)+"/";
    Run_props=open_run_properties(run,"macros/Runs_list.xlsx")

    ADC_raw=open_run_var(path,"RawADC",Run_props["Channels"])
    
    Pedestal=do_run_things(ADC_raw,compute_Pedestal)
    ADC=do_run_things((ADC_raw,Pedestal,Run_props["Polarity"]),substract_Pedestal)
    
    del ADC_raw,Run_props
    gc.collect()#free memory
    
    save_run_var(Pedestal,path,"Pedestal")
    save_run_var(ADC,path,"ADC")
    del Pedestal,ADC,
    gc.collect()#free memory

