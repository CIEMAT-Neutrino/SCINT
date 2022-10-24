# CYTHON_TOOLS
This is a python library to process and analyse raw data from the IR02 lab.

We want:

    -Classless structure, dictionaries hold all the run/channels information + the wvfs.
    
    -To avoid as much overcalculation as posible, in particular: produce pedestal/charge/time values once and store them sepparatly from the raw data to prevent memmory issues when dealing with multiple runs. 

We don't want:

    -Complicated hyerarchies
    -Comented/uncomented lines with the same code but different runs/configs


Rodrigo & Sergio
November 2022