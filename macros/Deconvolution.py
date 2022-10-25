import sys
sys.path.insert(0, '../')

from lib.my_functions import load_npy,load_average_npy
from lib.dec_functions import deconvolve
from lib.dec_functions import deconvolve

my_runs = load_npy([26],[6])
dec_runs = load_average_npy([10],[6])
OPT = {"LOGY":False}

# print(dec_runs[10][0].keys())
# KERNEL = dec_runs["ADC"]

deconvolve(my_runs,dec_runs[10][6]["ADC"],80,200,OPT)