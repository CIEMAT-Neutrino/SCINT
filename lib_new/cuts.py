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
    
    return pd.concat(aux,axis=1).sort_index(axis=1)

def SWAP_COLUM_LEVELS(DF: pd.DataFrame):
    return DF.swaplevel(0,1,1).sort_index(1)


def Apply_cut_toVAR(df:pd.DataFrame,VAR)->dict:
    
    aux_VAR=copy.deepcopy(VAR) #copy
     
    cut_as_dict=df.to_dict('series')
    if type(VAR[  list(VAR.keys())[0]  ])==dict: #nested dictionaries, apply on subdictionary
        for channel in VAR:
            for var in VAR[channel]: 
                aux_VAR[channel][var]=VAR[channel][var][cut_as_dict[channel]]
        return aux_VAR;
    else:#single dictionary, one key per channel
        for channel in VAR:
            aux_VAR[channel]=VAR[channel][cut_as_dict[channel]]
        return aux_VAR;