# CYTHON_TOOLS
This is a python library to process and analyse raw data from the IR02 lab.

We want:

    -Classless structure, dictionaries hold all the run/channels information + the wvfs.   
    -To avoid as much overcalculation as posible, in particular: 
        -Calculate pedestal/charge/time values all at once and store them sepparatly from the raw data
        -Prevent excessive memmory usage when dealing with multiple runs. 

We don't want:

    -Complicated hyerarchies
    -Comented/uncomented lines with the same code but different runs/configs

1. To start run:

    ./scripts/setup.sh
    then place all your root files in data/raw folder (check copy_data.sh for ideas)

2. Run the following macros from the macros folder:
    - macros/Root2Np.py
    - macros/Process.py
    - macros/Average.py
    - macros/Vis.py
    - macros/Calibration.py (should be upgarded to notebook allowing for interactive cuts)
    
3. To better visualize what is happening and perform non standard analysis, there are jupyter notebooks available in notebooks/

Rodrigo & Sergio & Andrés & Laura
November 2022

![alt text](https://imgflip.com/i/72cpdl)
