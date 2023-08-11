# SCINT (Sensor Calibration Interface for Neutrino Team!)

[![Documentation Status](https://readthedocs.org/projects/cython-tools/badge/?version=latest)](https://cython-tools.readthedocs.io/en/latest/?badge=latest)

:book: :page_with_curl: Access the [DOCUMENTATION](https://cython-tools.readthedocs.io/en/latest/) for more information :page_with_curl: :book:

:construction:
Work in progress (check [TO DO LIST](https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS/blob/main/To_Do.md))
:construction:

This is a python library to process and analyse raw data from the IR02 lab.

We want:

* Classless structure, dictionaries hold all the run/channels information + the wvfs.
* To avoid as much overcalculation as posible, in particular:
  * Calculate pedestal/charge/time values all at once and store them sepparatly from the raw data
  * Prevent excessive memmory usage when dealing with multiple runs.

We don't want:

* Complicated hyerarchies
* Comented/uncomented lines with the same code but different runs/configs

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

* Create a folder for your coustom scripts and notebooks and add them to the .gitignore file:

```bash
mkdir <your_folder_name>
echo "<your_folder_name/*>" >> .gitignore
```

* Create a folder for your data in data/MONTH/raw or use the copy_data.sh script to copy the data from the server.

```bash
mkdir data/MONTH/raw/<your_folder_name>
```

* Go to the scripts folder:
  
```bash
cd scripts
```

* Setup all the utilities needed for the macros:

```bash
sh setup.sh 
```

There is a MergeDebug script where there have been defined the actions to be checked in order to commit the changes to the GitHub repository, making sure everything works as before the changes. (check it for ideas on how to run the scripts)

2 Run the following macros FROM the macros folder:

```bash
cd ../macros
python3 00Raw2Np.py MergeDebug
python3 01PreProcess.py MergeDebug 
python3 02Process.py MergeDebug
python3 03Integration.py MergeDebug
python3 04Calibration.py MergeDebug
python3 05Scintillation.py MergeDebug
python3 06Deconvolution.py MergeDebug
python3 0XVisEvent.py MergeDebug 1 0,1
```

3 To better visualize what is happening and perform non standard analysis, there are jupyter notebooks available in notebooks/

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
