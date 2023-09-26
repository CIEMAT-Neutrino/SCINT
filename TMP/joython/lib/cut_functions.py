"""This Library provides basic interface for cuts. Dictionarys(channels and vars) are converted to pandasDataframes with Multiindexing [channel][variable]
"""
import pandas as pd
import copy 

def VARsAsDataFrame(VARs:tuple) -> pd.DataFrame:
    """Transforms a tuple of input variables into a multiindexed pandas dataframe (easier to perform cuts with)

    Args:
        VARs (tuple): Input variables, listed as tuple

    Returns:
        pd.DataFrame: DataFrame of linked variables, shared index axis (number of events)
    """
    if not type(VARs)==tuple:
        raise TypeError('bad type, use tuple as input (even for 1 variable)')
    aux=[]
    for VAR in VARs:
        reform  = {(outerKey, innerKey): values for outerKey, innerDict in VAR.items() for innerKey, values in innerDict.items()} #tuple as pairs to go multiindex
        pd1=pd.DataFrame(reform)
        aux.append(pd1)
    
    return pd.concat(aux,axis=1).swaplevel(0,1,1).sort_index(axis=1)

def SWAP_COLUM_LEVELS(DF: pd.DataFrame):#in a multiindexed dataframe, swaps order of the columns labels: df[var][ch] to df[ch][var] and vice-versa
    return DF.swaplevel(0,1,1).sort_index(1)


def Apply_cut_to_VAR(df:pd.DataFrame,VAR:dict)->dict:
    """This interface provides link between nice pandas df structure for cuts, and previous setup for channels and variables
    
    Args:
        df (pd.DataFrame): A data frame  as provided by 

    Returns:
        pd.DataFrame: DataFrame of linked variables, shared index axis (number of events)

    """
    
    aux_VAR=copy.deepcopy(VAR) #copy
     
    cut_as_dict=df.to_dict('series')
    if type(VAR[  list(VAR.keys())[0]  ])==dict: #nested dictionaries, apply on subdictionary
        for channel in VAR:
            for var in VAR[channel]: 
                aux_VAR[channel][var]=VAR[channel][var][cut_as_dict[channel]]
            print("Cut in ch",channel,":",VAR[channel][var].shape, aux_VAR[channel][var].shape)
        return aux_VAR;
    else:#single dictionary, one key per channel
        for channel in VAR:
            aux_VAR[channel]=VAR[channel][cut_as_dict[channel]]
        print("Cut in ch",channel,":",VAR[channel].shape, aux_VAR[channel].shape)
        return aux_VAR;