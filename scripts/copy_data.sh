#!/bin/bash

#Script must be run from main folder or paths will be messed up

#create data directory if not present
if [ ! -d "data" ]; then
mkdir ../data
fi

#raw data .root and .npy
if [ ! -d "data/raw" ]; then
mkdir ../data/raw
fi

#Analized data (charge, pedestal, peak...) variables
if [ ! -d "data/ana" ]; then
mkdir ../data/ana
fi

#Average wvfs 
if [ ! -d "data/ave" ]; then
mkdir ../data/ave
fi

#Doconvolved wvfs 
if [ ! -d "data/dec" ]; then
mkdir ../data/dec
fi

#Fitted wvfs 
if [ ! -d "data/fit" ]; then
mkdir ../data/fit
fi

# runes de interes feb22_2: calib(1,2,3) laser(9,10,11) alpha(25,26,27)
# runes de interes feb22: calib(1,2,3) laser(45,46,47) alpha(12,13,14)

# for n in "01" "02" "03" "12" "13" "14" "45" "46" "47";
for n in "12";
do
    scp -r pcae146:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22/ROOT/run${n}_ch* data/raw/.
done