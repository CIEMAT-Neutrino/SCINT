import sys
sys.path.insert(0, '../')

import pandas as pd
from lib.first_data_process import Bin2Np_excel

# in_path ="/media/rodrigoa/2Gb/data/SBND_XA_PDE/SBND_XA_VIS/raw/"
in_path ="/media/rodrigoa/DiscoDuro/SBND_XA_VIS/"
out_path="/media/rodrigoa/DiscoDuro/SBND_XA_VIS/joython/"

Bin2Np_excel("Runs_list.xlsx",compressed=False,i_path=in_path,o_path=out_path)
