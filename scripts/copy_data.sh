#!/bin/usr/env bash

#Script must be run from main folder or paths will be messed up

#create data directory if not present
if [ ! -d "../data" ]; then
mkdir ../data
fi

#raw data .root and .npy
if [ ! -d "../data/raw" ]; then
mkdir ../data/raw
fi

#Analized data (charge, pedestal, peak...) variables
if [ ! -d "../data/ana" ]; then
mkdir ../data/ana
fi

#Average wvfs 
if [ ! -d "../data/ave" ]; then
mkdir ../data/ave
fi

#Doconvolved wvfs 
if [ ! -d "../data/dec" ]; then
mkdir ../data/dec
fi

#Fitted wvfs 
if [ ! -d "../data/fit" ]; then
mkdir ../data/fit
fi

# runes de interes feb22_2: calib(1,2,3)    laser(9,10,11)  alpha(25,26,27)
# runes de interes feb22:   calib(1,2,3)    laser(45,46,47) alpha(12,13,14)
# runes de interes jan22:   calib(1,2,3)    laser(55,56,57) alpha(12,13,14)
# runes de interes dic21:   calib(18,19,20) laser(48,49,50) alpha(62,63,64)

# Write all runs inside the scp command to avoid inserting password more than once
scp -r pcae182:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run{"01","02","03","09","10","11","25","26","27"}_ch* ../data/raw/.
scp -r pcae182_outside:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run{"01","02","03","09","10","11","25","26","27"}_ch* ../data/raw/.