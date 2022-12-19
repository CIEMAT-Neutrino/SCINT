import sys
sys.path.insert(0, '../')

from lib.io_functions import load_npy,save_proccesed_variables
from lib.fit_functions import fit_wvfs

# import matplotlib.pyplot as plt
# import numpy as np

runs     = [25,26,27]     
channels = [4]       

my_runs = load_npy(runs,channels,"Average_","../data/ave/")

thrld = 1e-6
range = [80,1000] # Fit range in units of array length defined left and right from the max (peak of the wvf)

OPT = {
        "SHOW":True,
        "LOGY":True,
        "NORM":True
      }

key = ["AveWvf"]

fit_wvfs(my_runs,"SCINT",thrld,range,key,OPT)

save_proccesed_variables(my_runs,"Fit_","../data/fit/")