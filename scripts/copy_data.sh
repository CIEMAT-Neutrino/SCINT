#!/bin/bash

#Script must be run from main folder or paths will be messed up

#create data directory if not present
if [ ! -d "data" ]; then
mkdir data
fi

#raw data .root and .npy
if [ ! -d "data/raw" ]; then
mkdir data/raw
fi

#Analized data (charge, pedestal, peak...) variables
if [ ! -d "data/ana" ]; then
mkdir data/ana
fi

#Average wvfs 
if [ ! -d "data/ave" ]; then
mkdir data/ave
fi

#runes de interes: 2, 10, 22, 26

scp -r pcae146.ciemat.es:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run{"02","10","22","26"}_ch* ../data/
