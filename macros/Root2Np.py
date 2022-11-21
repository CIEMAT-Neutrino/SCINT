import sys
sys.path.insert(0, '../')
from lib.io_functions import root2npy

# Arrays used in load_run
RUNS    = [1,5,12]
# CH=[0,1,4,6] # SiPM1, SiPM2, PMT, XA
CH      = [0]

root2npy(RUNS,CH)