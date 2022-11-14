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

#Fitted wvfs 
if [ ! -d "data/fit" ]; then
mkdir data/fit
fi

#Deconvolved wvfs 
if [ ! -d "data/dec" ]; then
mkdir data/dec
fi

pip3 install -r requirements.txt