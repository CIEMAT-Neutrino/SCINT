# CYTHON_TOOLS
This is a python library to process and analyse raw data from the IR02 lab.

We want:

    -Classless structure, dictionaries hold all the run/channels information + the wvfs.
    
    -To avoid as much overcalculation as posible, in particular: produce pedestal/charge/time values once and store them sepparatly from the raw data to prevent memmory issues when dealing with multiple runs. 

We don't want:

    -Complicated hyerarchies
    -Comented/uncomented lines with the same code but different runs/configs

1. To start make the folder data/raw and and place there your root files
2. Make additional subfolders: data/ana and data/ave
3. Run the following macros from the macros folder:
    - macros/Root2Np.py
    - macros/Process.py
    - macros/Average.py
    - macros/Vis.py

Rodrigo & Sergio
November 2022
