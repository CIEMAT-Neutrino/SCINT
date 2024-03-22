#!/bin/bash

# The confirmation message need to be run with $ bash setup.sh (this lines are to allow $ sh setup.sh too)
if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi

#Script must be run from SCRIPTS folder or paths will be messed up
echo -e "\e[31mWARNING: Only run this script from project's root directory!\e[0m"
# Ask if sure to continue
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
# If the user did not answer with y, exit the script
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Create the data folder if not present
if [ ! -d "../data" ]; then
echo -e "\e[36mCreating data folder... \e[0m"
mkdir data
fi

# Ask if data should be mounted to /pc/choozdsk01/DATA/SCINT
read -p "Do you want to mount the data folder to /pc/choozdsk01/DATA/SCINT? (y/n) " -n 1 -r
echo
# If the user did not answer with y, exit the script
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Mount without sudo
    ln -s /pc/choozdsk01/DATA/SCINT data
    echo -e "\e[36mData folder mounted to /pc/choozdsk01/DATA/SCINT \e[0m"
fi


# copy notebooks folder if not present
# if [ -d "../notebooks" ]; then
# echo -e "\e[31mWARNING: notebooks folder NOT updated. Delete it if you want to update it. \e[0m"
# fi

# if [ ! -d "../notebooks" ]; then
# echo -e "\e[36mCreating notebooks... \e[0m"
# cp -r ../vault/notebooks ../src/notebooks
# rm -rf ../src/notebooks/cleaning
# rm -rf ../src/notebooks/__pycache__
# fi


# If you already have the packages installed (i.e. .venv with VSCode), you can skip this step
read -p "Do you want to INSTALL the packages (y/n)?" -n 1 -r
echo
# If the user did not answer with y, exit the script
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    # Update pip inside python virtual environment
    echo -e "\e[36mUpdating pip... \e[0m"
    pip3 install --upgrade pip
    echo -e "\e[36mInstalling packages... \e[0m"
    pip3 install -r src/requirements.txt
fi