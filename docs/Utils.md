# 🔧 **UTILS** 

## 💡 TIPS <a ID="git"></a>
* Install [python](https://www.python.org/downloads/) and [pip3](https://bootstrap.pypa.io/get-pip.py)
* If you are new to python and jupyter notebooks check this references:
    - [Python](https://www.python.org/about/gettingstarted/)
    - [Jupyter Notebooks](https://jupyter-notebook.readthedocs.io/en/latest/notebook.html#introduction)
    - [Code Academy](https://www.codecademy.com/learn/learn-python-3)

* If you need to **take data** you may find useful our following repositories:
    - [DAQ Software](https://github.com/CIEMAT-Neutrino/wavedump-3.10.0)
    - [Graphical User Interface](https://github.com/CIEMAT-Neutrino/WaveDumpConfig_V3)

* To update the repository you have cloned you can run the following commands in a terminal:
    ```bash
    git status                         # Changes in your files. You can choose to add them (commit them) or ignore them (checkout)
    git fetch                          # Updates the working tree with the repository in GitHub
    git pull                           # Dowloads the updates to your local copy
    git checkout -b <your_branch_name> # Creates a new branch
    ```
    More commands and info in the web ([git-cheat_sheet](https://about.gitlab.com/images/press/git-cheat-sheet.pdf))

### Mounting/umounting a /pnfs/ or /pc/ folder in your local computer (from macros folder)
```bash
sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/your_folder ../data
sshfs pcaeXYZ:/pc/choozdsk01/palomare/SCINT/ ../data

sudo umount ../data
fusermount -u data/ # If sudo not available, use fusermount
```

### Setup ROOT environment
```bash
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.24.08/x86_64-centos7-gcc48-opt/bin/thisroot.sh 
```

### Changing permissions on files
```bash
sudo sshfs -o allow_other USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/your_folder ../data
chmod o=rwx */*.npz
chmod -R ugo=+rwx folder #POWERFUL: everything in the folder will have all permissions for everyone
```

### Transform the npx files to another format
```bash
import numpy as np
data = np.load(filename)
for key, value in data.items(): np.savetxt("somepath" + key + ".csv", value)
```

### Optionals

* Specify correct Python version when creating virtual environment
    ```bash
    python -m venv venv
    ```
* Activate on Unix or MacOS
    ```bash
    source venv/bin/activate
    ```
* Deactivate virtual environment
    ```bash
    deactivate
    ```
* Activate on Windows (cmd.exe)
    ```bash
    venv\Scripts\activate.bat
    ```
* Activate on Windows (PowerShell)
    ```bash
    venv\Scripts\Activate.ps1
    ```
* Install the modules in your requirements.txt file (optional)
    ```bash
    pip install -r requirements.txt
    ```
* Update your requirements.txt file
    ```bash
    pip freeze > requirements.txt
    ```
* Remove the old virtual environment folder: macOS and Linux
    ```bash
    rm -rf venv
    ```
* Remove the old virtual environment folder: Windows
    ```bash
    rd /s /q "venv"
    ```