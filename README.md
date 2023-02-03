# CYTHON_TOOLS

:construction: 
Work in progress (check [TO DO LIST](https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS/blob/main/To_Do.md))
:construction:

This is a python library to process and analyse raw data from the IR02 lab.

We want:
* Classless structure, dictionaries hold all the run/channels information + the wvfs.   
* To avoid as much overcalculation as posible, in particular:
    - Calculate pedestal/charge/time values all at once and store them sepparatly from the raw data
    - Prevent excessive memmory usage when dealing with multiple runs. 

We don't want:
* Complicated hyerarchies
* Comented/uncomented lines with the same code but different runs/configs

0. Download
    Just clone the repository into a local directory.
    ```
    git clone https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS.git 
    ```

1. To start RUN:
    ```
    cd scripts
    ```

    Setup all the utilities needed for the macros:
    ```
    ./scripts/setup.sh 
    ```
    
    Then place all your root files in data/raw folder (check copy_data.sh for ideas and run)
    ```
    ./scripts/copy_data.sh
    ```
    
    There is a MergeDebug script where there have been defined the actions to be checked in order to commit the changes to the GitHub repository, making sure everything works as before the changes. (check it for ideas on how to run the scripts)
    ```
    sh ../scripts/MergeDebug.sh
    ```

2. Run the following macros FROM the macros folder:
    ```
    cd macros
    ```
    - macros/00Raw2Np.py
    ```
    python 3 00Raw2Np.py MergeDebug
    ```

    - macros/01PreProcess.py
    ```
    python 3 01PreProcess.py MergeDebug
    ```

    - macros/02PreProcess.py
    ```
    python 3 02Process.py MergeDebug
    ```

    - macros/03Calibration.py
    ```
    python 3 03Calibration.py MergeDebug
    ```

    - macros/0XVisEvent.py or macros/0XVisTests.py (whenever you want! (once you pre-process))
    ```
    python 3 0XVisEvent.py MergeDebug 1 0,1
    ```

    
3. To better visualize what is happening and perform non standard analysis, there are jupyter notebooks available in notebooks/

:book: :page_with_curl: Access the [DOCUMENTATION](https://.github.io/CIEMAT-Neutrino/CYTHON_TOOLS/blob/laura/documentation/index.html) for more information :page_with_curl: :book:

Rodrigo & Sergio & Andrés & Laura
November 2022

![alt text](https://i.imgflip.com/72cpdl.jpg)


