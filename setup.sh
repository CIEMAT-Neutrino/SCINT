#!/bin/bash

# The confirmation message need to be run with $ bash setup.sh (this lines are to allow $ sh setup.sh too)
if [ ! "$BASH_VERSION" ]; then
    exec /bin/bash "$0" "$@"
fi

#Script must be run from SCRIPTS folder or paths will be messed up
echo -e "\e[31mWARNING: Only run this script from project's root directory!\e[0m"
# Ask if sure to continue
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
# If the user did not answer with y, exit the script
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create the data folder if not present else ask if it should be unmounted
if [ -d "data" ]; then
    read -p "Data folder already exists. Do you want to unlink it? (y/n) " -n 1 -r
    echo
    # If the user did not answer with y, exit the script
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Unmount without sudo
        unlink data
        echo -e "\e[36mData folder unlinked \e[0m"
    fi
fi

# Ask if data should be mounted to /pc/choozdsk01/DATA/SCINT
read -p "Do you want to link the data folder to /pc/choozdsk01/DATA/SCINT/TUTORIAL? (y/n) " -n 1 -r
echo
# If the user did not answer with y, exit the script
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Mount without sudo
    ln -s /pc/choozdsk01/DATA/SCINT/TUTORIAL data
    echo -e "\e[36mData folder linked to /pc/choozdsk01/DATA/SCINT/TUTORIAL \e[0m"
fi
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    # Ask for differnt path to mount
    read -p "Enter the path to link the data folder: " -r
    # Mount without sudo
    ln -s $REPLY data
fi

# Check if the .venv directory exists and activate it
if [ -d .venv ]; then
    echo -e "\e[36mActivating the virtual environment... \e[0m"
    source .venv/bin/activate

    # If you already have the packages installed (i.e. .venv with VSCode), you can skip this step
    read -p "Do you want to INSTALL the packages (y/n)?" -n 1 -r
    echo
    # If the user did not answer with y, exit the script
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Update pip inside python virtual environment
        echo -e "\e[36mUpdating pip... \e[0m"
        pip3 install --upgrade pip
        echo -e "\e[36mInstalling packages... \e[0m"
        pip3 install -r srcs/requirements.txt
    fi

else # If the .venv directory does not exist, create it
    echo -e "\e[36mCreating the virtual environment... \e[0m"
    source srcs/scripts/make_python_env.sh
fi