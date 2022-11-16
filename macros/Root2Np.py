import sys
sys.path.insert(0, '../')
from lib.io_functions import root2npy

RUNS=[9,10,11,25,26,27]
RUNS_CALIB=[1,2,3]

CH=[0,1,4,6]
CH_CALIB=[0,1,6] #4 is the PMT


for run in RUNS:
    for ch in CH:
        root2npy("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".root","../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy")

for run in RUNS_CALIB:
    for ch in CH_CALIB:
        root2npy("../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".root","../data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy")