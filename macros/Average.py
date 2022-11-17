import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,delete_keys,save_proccesed_variables
from lib.wvf_functions import average_wvfs,integrate_wvfs
from itertools import product

# RUNS=[35,36,37,55,56,57]
RUNS_CALIB=[1,2,3]

# CH=[0,1,5,6]
CH_CALIB=[0,1,2,3,4]       

DELETE_KEYS = ["Ana_ADC"]

# for run, ch in product(RUNS,CH):
#     # Start load_run 
#     my_runs = load_npy([run],[ch],"Analysis_","../data/ana/")
#     average_wvfs(my_runs)
#     integrate_wvfs(my_runs,"AVE_INT_LIMITS","AvWvf")
#     save_proccesed_variables(my_runs,"Analysis_","../data/ana/")
    
#     delete_keys(my_runs,DELETE_KEYS)
#     save_proccesed_variables(my_runs,"Average_","../data/ave/")

for run, ch in product(RUNS_CALIB,CH_CALIB):
    # Start load_run 
    my_runs = load_npy([run], [ch],"Analysis_","../data/ana/") 
    average_wvfs(my_runs)
    integrate_wvfs(my_runs,"AVE_INT_LIMITS","AvWvf")
    save_proccesed_variables(my_runs,"Analysis_","../data/ana/")
    
    delete_keys(my_runs,DELETE_KEYS)
    save_proccesed_variables(my_runs,"Average_","../data/ave/")