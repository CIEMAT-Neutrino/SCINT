import numpy as np

from .io_functions import load_npy,check_key
from itertools import product

def rand_scint_times(n, fast = 6e-9, slow = 1e-6, ratio = 0.25):
    """ 
    This function is a randon number generator that returns a sorted nparray of photon arrival times according to a given scintilation profile.
    VARIABLES:
        - n: (int) number of produced times.
        - fast: (float) tau value of fast scint component -- default: 6e-9 [s]
        - slow: (float) tau value of slow scint component -- default: 1e-6 [s]
        - ratio: (float) ratio of the scint components sholud be [0,1] -- default: 0.25
    """
    if ratio < 0 or ratio > 1: print("WARNING: ratio should be between 0 and 1!!!")    

    aux = np.random.uniform(low = 0, high = 1, size = n)
    # offset = np.random.random() #photon can arrive at any time
    array = fast + (aux < (ratio)) * np.random.exponential(scale = fast, size = n) + (aux > (ratio)) * np.random.exponential(scale = slow, size = n)
    array = np.sort(array)
    return array