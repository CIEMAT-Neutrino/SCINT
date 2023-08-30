#!/bin/usr/env bash
input_file="$1"
## RUN --> sh ../scripts/MergeDebug.sh 
## Make sure you have at least RUNS{1,9,25,29}+CH{0,6} in data/raw/*.root #

echo "----------------------------------------------------------------------------------------------"
echo "----------------------------- (: WELCOME TO THE DEBUG SCRIPT :) ------------------------------"
echo "- We recommend to use the input/MergeDebug.txt file to try the macros before merging branches -"
echo "----------------------------------------------------------------------------------------------"

## 00Raw2Np.py --> loads raw data + save into /data/MONTH/npy/
echo "\n------------------ Testing Root2Np.py ------------------"
python3 ../macros/00Raw2Np.py -i ${input_file} -d True
echo "\n------ Expected output{Saved data in: ../data/MONTH/npy/runXX_chY/RAW_NAME_BRANCH.npy}. Everything OK ------"

# ## 01PreProcess.py --> pre-process raw waveforms and save PEDESTAL/PEAK variables
echo "\n------------------ Testing PreProcess.py ------------------"
python3 ../macros/01PreProcess.py -i ${input_file} -d True
echo "\n------ Expected output{Saved data in: ../data/MONTH/npy/runXX_chY/NAME_BRANCH.npy}. Everything OK ------"

# ## 02Process.py --> process wvfs with raw pedesatal/peak info to get the ANA wvf with BASELINE/PCH changed
echo "\n------------------ Testing Process.py ------------------"
python3 ../macros/02Process.py -i ${input_file} -d True
echo "\n------ Expected output{Saved data in: ../data/MONTH/npy/runXX_chY/ANA_NAME_BRANCH.npy}. Everything OK ------"

# ## 03Integration.py --> integrates charge
# echo "\n------------------ Testing Integration.py ------------------"
# python3 ../macros/03Integration.py -i ${input_file} -d True
# echo "\n------ Expected output{FIT_PLOT + SPE gauss parameters X Y Z + ../fit_data/gain_chX.txt}. Everything OK ------"

# ## 04Calibration.py --> calibrate (calibration runs) and obtain gain values in txt
# echo "\n------------------ Testing Calibration.py ------------------"
# python3 ../macros/04Calibration.py MergeDebug 1 0,6
# echo "\n------ Expected output{FIT_PLOT + SPE gauss parameters X Y Z + ../fit_data/gain_chX.txt}. Everything OK ------"

## 0XVisTests.py --> visualize event by event the selected runs&channels
# echo "\n------------------ Testing Vis.py ------------------"
# python3 ../macros/0XVisEvent.py MergeDebug 1 0,6
# echo "\n------ Expected output{PLOT}. Everything OK ------"

## 05Scintillation.py --> perform charge analysis
# echo "\n------------------ Testing Scintillation.py ------------------"
# python3 ../macros/05Scintillation.py MergeDebug 25 0
# echo "\n------ Expected output{PLOT}. Everything OK ------"

## 06Deconvolution.py --> perform deconvolution
# echo "\n------------------ Testing Deconvolution.py ------------------"
# python3 ../macros/06Deconvolution.py MergeDebug
# echo "\n------ Expected output{PLOT}. Everything OK ------"