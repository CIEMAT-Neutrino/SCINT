#!/bin/bash

#Script must be run from scripts folder or paths will be messed up

# copy notebooks folder if not present
if [ -d "../notebooks" ]; then
echo "\033[0;31m" WARNING: notebooks folder NOT updated. Delete it if you want to update it. '\033[0m'
fi

if [ ! -d "../notebooks" ]; then
echo "\033[0;36m" Copying notebooks... '\033[0m'
cp -r ../vault/notebooks ../notebooks
rm -rf ../notebooks/cleaning
fi
fi


### COMMON VIRTUAL ENVIROMENT TO RUN THE MACROS ###
# source /pnfs/ciemat.es/data/neutrinos/venv_python3.7/bin/activate 
pip install --upgrade pip
pip3 install -r requirements.txt
#sudo apt install <requirementsTeX.txt
#deactivate 

echo "\033[0;32m" SUCCESS! '\033[0m'

# Next run:
# sshfs USER@pcaeXXX.ciemat.es:/pnfs/ciemat.es/data/neutrinos/SBND_XA_PDE ../data