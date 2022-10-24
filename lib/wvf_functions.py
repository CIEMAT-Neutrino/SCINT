import copy
import numpy as np

def save_proccesed_variables(my_runs,out_path="data/Analysis_"):
    """Does exactly what it says, no RawWvfs here"""
    
    #  Remove the unwanted branches in the copy
    aux=copy.deepcopy(my_runs)
    print(my_runs[10][0].keys())
    print(aux [10][0].keys())

    for run in aux["N_runs"]:
        for ch in aux["N_channels"]:
            x=0
            for key in aux[run][ch]["Raw_file_keys"]:
                del aux[run][ch][key]

    # Crosscheck
    print(my_runs[10][0].keys())
    print(aux [10][0].keys())
    
    # Save the info in aux dict
    for run in aux["N_runs"]:
        for ch in aux["N_channels"]:
            aux_path=out_path+"run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"
            np.save(aux_path,aux[run][ch])
            print("Saved data in:" , aux_path)