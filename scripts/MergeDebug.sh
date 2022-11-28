#!/bin/bash

# RUN --> sh ../scripts/MergeDebug.sh 
# Make sure you have RUNS{1,9,25,29}+CH{0,6} in data/raw/*.root #

echo "\n----------------------------------------------------------------------------------------------"
echo "\n----------------------------- (: WELCOME TO THE DEBUG SCRIPT :) ------------------------------"
echo "\n We recommend to use the input/MergeDebug.txt file to try the macros before merging branches."
echo "\n----------------------------------------------------------------------------------------------"
echo "\n"

# Root2Np.py --> loads .root + save into /data/raw/*.npy + pre-process
echo "\n------------------ Testing Root2Np.py ------------------"
python3 ../macros/Root2Np.py
echo "\n------ Expected output{Saved data in: ../data/raw/runXX_chY.npy}. Everything OK ------"


#Process.py --> process waveforms and save in /data/ana/
echo "\n------------------ Testing Process.py ------------------"
python3 ../macros/Process.py
echo "\n------ Expected output{Saved data in: ../data/ana/Analysis_runXX_chY.npy}. Everything OK ------"

# Average.py --> process waveforms and save in /data/ana/
echo "\n------------------ Testing Average.py ------------------"
python3 ../macros/Average.py
echo "\n------ Expected output{Saved data in: ../data/ave/Average_runXX_chY.npy}. Everything OK ------"


#Calibration.py --> calibrate (calibration runs)
echo "\n------------------ Testing Calibration.py ------------------"
python3 ../macros/Calibration.py
echo "\n------ Expected output{PLOT + SPE gauss parameters X Y Z; Saved data in: ../data/ana/Analysis_runXX_chY.npy; Saved data in: ../data/ave/Average_runXX_chY.npy}. Everything OK ------"


#Vis.py --> visualize event by event the selected runs&channels
echo "\n------------------ Testing Vis.py ------------------"
python3 ../macros/Vis.py
echo "\n------ Expected output{PLOT}. Everything OK ------"