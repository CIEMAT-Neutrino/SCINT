import sys
sys.path.insert(0, '../')

import pandas as pd
from lib_new.first_data_process import Bin2Npz_excel

Bin2Npz_excel("Runs_list.xlsx")
