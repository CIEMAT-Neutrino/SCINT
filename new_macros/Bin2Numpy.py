import sys
sys.path.insert(0, '../')

import pandas as pd
from lib_new.first_data_process import Bin2Np_excel

Bin2Np_excel("Runs_list.xlsx")
