# This library processes the runs and channel structure neccesary for everything else
# Simplicity is the key

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '../')


def open_run_var(run_path,var_name,channels,compressed=True):

    run_var=dict();
    
    for ch in channels:
        
        if compressed: 
            full_path = run_path+var_name+"_ch"+str(ch)+".npz"
            run_var[ch]=np.load(full_path ,allow_pickle=True,mmap_mode='r') ["arr_0"]
            if run_var[ch].shape==():# we are loading a dictionary
                run_var[ch]=run_var[ch].item()
        else: 
            full_path = run_path+var_name+"_ch"+str(ch)+".npy"
            run_var[ch]=np.load(full_path ,allow_pickle=True)
            if run_var[ch].shape==():# we are loading a dictionary
                run_var[ch]=run_var[ch].item()

    return run_var;

def open_run_properties(run,excel_file_path="",sheet='Sheet1'):
    """Creates a dictionary with run properties out of an exel table

    Args:
        run (int):number of the run
        excel_file_path (str): excel containing the runs table data sheet. Defaults to "".
        sheet (str, optional):sheet in the excel file. Defaults to 'Sheet1'.

    Returns:
        Dictionary with run properties: polarity, type of run, thresholds, aprox duration... etc can be computed here
    """
    df = pd.read_excel(excel_file_path, sheet_name=sheet,engine='openpyxl')
    df['Channels'] = df['Channels'].apply(lambda x: list(map(int,x.split(" ")))) #excell only allows one value per cell, convert channels from string to array of ints
    df['Polarity'] = df['Polarity'].apply(lambda x: list(map(int,x.split(" "))))
    props=df.loc[df['Run'] == run].to_dict(orient='records')[0]
    
    props['Polarity'] = dict(zip(props['Channels'],props['Polarity'])) #map polarity with channels
    
    return props

def save_run_var(run_var,run_path,var_name,compressed=True):
    channels=run_var.keys()

    print("----------")
    for ch in channels:
        
        if compressed:
            full_path = run_path+var_name+"_ch"+str(ch)+".npz"
            np.savez_compressed(full_path,run_var[ch])
    
        else: 
            full_path = run_path+var_name+"_ch"+str(ch)+".npy"
            np.save(full_path,run_var[ch])
        
        print("Saving: ",var_name," channel:",ch, " ,in:",full_path)



def do_run_things(run,func):
    
    if type(run)== dict:#single variable passed here
        channels=run.keys()
        # Do stuff on every channel of the run
        things=dict()
        
        print("----------")
        for ch in channels: 
            print("Doing: ",func.__name__," on channel:",ch)
            things[ch]=func(run[ch]);
        
        return things

    elif type(run) == tuple:# we are facing multiple input variables
        channels=run[0].keys()

        # Do stuff on every channel of the run
        things=dict()

        print("----------")
        for ch in channels: 
            vars_ch=tuple(var[ch] for var in run) #prepare all the variables only in the selected channel

            print("Doing: ",func.__name__," on channel:",ch)
            things[ch]=func(vars_ch);
        
        return things
