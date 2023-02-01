import pandas as pd
from lib_new.first_data_process import Bin2Npz_excel

# df = pd.read_excel(r'Runs_list.xlsx', sheet_name='Sheet1')
# df['Channel']=df['Channel'].apply(lambda x: list(map(int,x.split(",")))) #excell only allows one value per cell, convert string to array of channels
Bin2Npz_excel("Runs_list.xlsx")
