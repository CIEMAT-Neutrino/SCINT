#!/bin/bash

#Script must be run from main folder or paths will be messed up

#create data directory if not present
if [ ! -d "../data" ]; then
mkdir ../data
fi

if [ ! -d "../fit_data" ]; then
mkdir ../fit_data
fi

pip3 install     -r requirements.txt
sudo apt install <requirementsTeX.txt

# Next run:
# sshfs USER@pcaeXXX.ciemat.es:/pnfs/ciemat.es/data/neutrinos/SBND_XA_PDE ../data