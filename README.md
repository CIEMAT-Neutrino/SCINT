# SCINT (Sensor Calibration Interface for Neutrino Team!)

[![Documentation Status](https://readthedocs.org/projects/scint/badge/?version=latest)](https://scint.readthedocs.io/en/latest/?badge=latest)

:book: :page_with_curl: Access the [DOCUMENTATION](https://scint.readthedocs.io/en/latest/) for more information :page_with_curl: :book:

:construction:
Work in progress (check [TO DO LIST](https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS/blob/main/To_Do.md))
:construction:

This is a Python library to process and analyze raw data from the IR02 lab.

We want:

* Classless structure, dictionaries hold all the run/channels variables (+ wvfs).
* To avoid as much overcalculation as possible:
  * Calculate pedestal/charge/time... values at once and store them separately from the raw data.
  * Prevent excessive memory usage when dealing with multiple runs by only loading the variables and not the wvfs.

We don't want:

* Complicated hierarchies
* Commented/uncommented lines with the same code but different runs/configs

0 Download

* Just clone the repository into a local directory.

```bash
git clone https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS.git 
```

1 To start RUN:

* Create your own branch:

```bash
git checkout -b <your_branch_name>
```

* Create a folder for your custom scripts and notebooks and add them to the .gitignore file:

```bash
mkdir <your_folder_name>
echo "<your_folder_name/*>" >> .gitignore
```

* Create a folder data/ (or use the copy_data.sh script) to copy the data from the server.

```bash
mkdir data/
sshfs user@server:path_to_data data
```

* Go to the scripts folder:
  
```bash
cd scripts
```

* Setup all the utilities needed for the macros:

```bash
sh setup.sh 
```

There is a MergeDebug script that checks the basic workflow before committing the changes to the GitHub repository, making sure everything works as before uploading any change.

2 Run the following macros FROM the macros folder:

```bash
cd ../macros
python3 00Raw2Np.py -i MergeDebug
python3 01PreProcess.py -i MergeDebug 
python3 02AnaProcess.py -i MergeDebug
python3 03Integration.py -i MergeDebug
python3 04Calibration.py -i MergeDebug
python3 05Scintillation.py -i MergeDebug
python3 06Deconvolution.py -i MergeDebug
python3 0XVisEvent.py -i MergeDebug -r 1 -c 0,1
```

3 To better visualize what is happening and perform non-standard analysis, there are Jupyter notebooks available in notebooks/

```bash
cd ../notebooks
jupyter notebook
```

## LICENSE
[MIT](https://choosealicense.com/licenses/mit/)

## Authors (alphabetical order, please insert your name here if you contribute to this project)

* [**Alvárez-Garrote, Rodrigo**](https://github.com/LauPM)
* [**de la Torre Rojo, Andrés**](https://github.com/andtorre)
* [**Manthey Corchado, Sergio**](https://github.com/mantheys)
* [**Pérez-Molina, Laura**](https://github.com/rodralva)

![alt text](https://i.imgflip.com/72cpdl.jpg)
