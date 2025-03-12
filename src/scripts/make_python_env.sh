# Create a python virtual environment (v3.7) and install the required packages from requirements.txt

# Make sure you are in the root directory of the project
# Project structure:
#   - src/scripts/make_env.sh

# Install python3.7
# Ask to be sure that you are in the correct directory
root_dir="/pc/choozdsk01/users/${USER}/SCINT/"

echo "Current directory: $(pwd)"
echo "Root directory: ${root_dir}"
echo "Are you in the root directory of the project? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ]; then
    echo "Great! Let's continue."
else
    echo "Please go to the root directory of the project and run the script again."
    exit 1
fi

# Create a virtual environment in the root directory ../../.venv
# Check if the .venv directory already exists
if [ -d .venv ]; then
    echo "The .venv directory already exists. Do you want to remove it? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        rm -rf .venv
        echo "The .venv directory is removed."
    else
        echo "Please remove the .venv directory and run the script again."
        exit 1
    fi
fi
mkdir .venv
cd .venv

/cvmfs/sft.cern.ch/lcg/releases/Python/3.7.3-f4f57/x86_64-centos7-gcc7-opt/bin/python3 -m venv .
source bin/activate

# Install the required packages
pip install --upgrade pip
pip install -r src/scripts/requirements.txt

echo "Virtual environment is created and the required packages are installed."
echo "To activate the virtual environment, run 'source .venv/bin/activate'."
echo "To deactivate the virtual environment, run 'deactivate'."
echo "To remove the virtual environment, delete the .venv directory."
