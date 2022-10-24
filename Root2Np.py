from lib.my_functions import root2npy

RUNS=[10,22,26]
RUNS_calib=["02"]

CH=[0,1,4,6]
CH_calib=[0,1,6] #4 is the PMT

for run in RUNS:
    for ch in CH:
        root2npy("data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".root","data/raw/run"+str(run).zfill(2)+"_ch"+str(ch)+".npy")