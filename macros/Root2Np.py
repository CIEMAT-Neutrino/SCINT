import sys
sys.path.insert(0, '../')
from lib.io_functions import root2npy

RUNS=[1,2,3,9,10,11,25,26,27]
CH=[0,1,4,6]

root2npy(RUNS,CH)