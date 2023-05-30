#!/bin/bash

#Script must be run from main folder or paths will be messed up

#create data directory if not present
if [ ! -d "../data" ]; then
mkdir -p ../data/MergeDebug/raw
mkdir -p ../data/MergeDebug/npy
fi

if [ ! -d "../fit_data" ]; then
mkdir ../fit_data
fi

if [ ! -d "../macros" ]; then
cp -r ../01TemplateMacros ../macros
fi

if [ ! -d "../notebooks" ]; then
cp -r ../02TemplateNbook ../notebooks
fi

### COMMON VIRTUAL ENVIROMENT TO RUN THE MACROS ###
# source /pnfs/ciemat.es/data/neutrinos/venv_python3.7/bin/activate 

pip install --upgrade pip
pip3 install    -r requirements.txt
#sudo apt install <requirementsTeX.txt

#deactivate 

echo SUCCESS!

# Next run:
# sshfs USER@pcaeXXX.ciemat.es:/pnfs/ciemat.es/data/neutrinos/SBND_XA_PDE ../data
