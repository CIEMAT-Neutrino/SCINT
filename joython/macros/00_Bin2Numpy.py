import sys
sys.path.insert(0, '../')

import pandas as pd
from lib.first_data_process import Bin2Np_excel

DEBUG=True
if DEBUG:import faulthandler; faulthandler.enable();


# ## First Week: Apsaia VIS
# in_path ="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/"
# out_path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VIS/joython/"
# run_table="APSAIA_VIS.xlsx"

## Second Week: Apsaia VUV
# in_path ="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/"
# out_path="/media/rodrigoa/DiscoDuro/SBND_XA_PDE/APSAIA_VUV/joython/"
# run_table="APSAIA_VUV.xlsx"

## Third Week: Dahpne VIS
in_path ="/scr/neutrinos/rodrigoa/DAPHNE_VIS/"
out_path="/scr/neutrinos/rodrigoa/DAPHNE_VIS/joython/compressed/"
run_table="APSAIA_VIS.xlsx"

Bin2Np_excel(run_table,compressed=True,i_path=in_path,o_path=out_path)
