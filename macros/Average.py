import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,delete_keys,save_proccesed_variables
from lib.wvf_functions import average_wvfs,integrate_wvfs
from itertools import product

# Arrays used in load_run
RUNS    = [1,12]     
# CH=[0,1,4,6] # SiPM1, SiPM2, PMT, XA     
CH      = [0,1]       

DELETE_KEYS = ["Ana_ADC"]
OPT  = {
    "PRINT_KEYS":     True
    }

for run, ch in product(RUNS,CH):
    # Start load_run 
    my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")
    average_wvfs(my_runs,OPT)

    integrate_wvfs(my_runs,"AVE_INT_LIMITS","AvWvf",["ADC", 250],[0,100])
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")
    
    delete_keys(my_runs,DELETE_KEYS)
    save_proccesed_variables(my_runs,"Average_","../data/ave/")