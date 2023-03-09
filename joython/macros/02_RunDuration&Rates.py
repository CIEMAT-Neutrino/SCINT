import sys
sys.path.insert(0, '../')

from lib.io_functions  import open_run_var,open_run_properties,do_run_things,save_run_var
from lib.ped_functions import compute_Pedestal,substract_Pedestal, compute_Peak


# path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/joython/"
path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"

for run in range(40):
    if run==3:continue
    
    Run_props=open_run_properties(run,"APSAIA_VUV.xlsx")
    run_path=path+"run"+str(run).zfill(2)+"/";

    compress=False
    
    
    # One channel at a time: 
    # loading all ch waveforms might demmand too much memory, 
    # remember to always delete between runs to prevent overloading)

    for ch in [Run_props["Channels"][0]]:
        TS=open_run_var(run_path,"Timestamp",[ Run_props["Channels"][0] ],compressed=compress)

        duration=(TS[Run_props["Channels"][0]][-1]-TS[Run_props["Channels"][0]][0])
        Nev=TS[Run_props["Channels"][0]].shape[0]
        print(Nev,duration,Nev/duration)
        

