import numpy as np

from .io_functions import load_npy,check_key
from itertools import product

def rand_scint_times(N=1000,fast=6e-9,slow=1e-6,ratio=0.25):
    aux=np.random.uniform(low=0,high=1,size=N)
    # offset = np.random.random() #photon can arrive at any time
    array = fast + (aux<(ratio))*np.random.exponential(scale=fast,size=N)+(aux>(ratio))*np.random.exponential(scale=slow,size=N)
    array = np.sort(array)
    return array