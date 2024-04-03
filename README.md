# SCINT (Sensor Calibration Interface for Neutrino Team!)

[![Documentation Status](https://readthedocs.org/projects/scint/badge/?version=latest)](https://scint.readthedocs.io/en/latest/?badge=latest)

:book: :page_with_curl: Access the [DOCUMENTATION](https://scint.readthedocs.io/en/latest/) for more information :page_with_curl: :book:

This is a Python library to process and analyze raw data from the lab.

We want:

* Classless structure, dictionaries hold all the run/channels variables (+ wvfs).
* To avoid as much overcalculation as possible:
  * Calculate pedestal/charge/time... values at once and store them separately from the raw data.
  * Prevent excessive memory usage when dealing with multiple runs by only loading the variables and not the wvfs.

We don't want:

* Complicated hierarchies
* Commented/uncommented lines with the same code but different runs/configs

0 Download

* Clone the repository into a local directory and create your branch:

```bash
git clone https://github.com/CIEMAT-Neutrino/SCINT.git
cd SCINT
git checkout -b <your_branch_name>
```

* You can create a `test` folder for your custom scripts or code.

* [OPTIONAL] Create a folder for your custom scripts and add them to the .gitignore file:

```bash
mkdir <your_folder_name>
echo "<your_folder_name/*>" >> .gitignore
```

1 To start RUN:

* Go to the scripts folder and set all the utilities needed for the macros:
  
```bash
cd SCINT/scripts
sh setup.sh 
```

* Create a folder data/ (or use the copy_data.sh script) to copy the data from the server.

```bash
mkdir data/
sshfs user@server:path_to_data data
```

2 Run the following macros FROM the macros' folder:

```bash
cd ../macros
python3 XXmacro.py (--flags input) 
```

3 To better visualize what is happening and perform non-standard analysis, there are Jupyter notebooks available in notebooks

```bash
cd ../notebooks
jupyter notebook 00TUTORIAL.ipynb
```

:construction:
Work in progress (check [TO DO LIST](https://github.com/CIEMAT-Neutrino/CYTHON_TOOLS/blob/main/To_Do.md))
:construction:

## LICENSE
[MIT](https://choosealicense.com/licenses/mit/)

## Authors (alphabetical order, please insert your name here if you contribute to this project)

* [**Alvárez-Garrote, Rodrigo**](https://github.com/rodralva)
* [**de la Torre Rojo, Andrés**](https://github.com/andtorre)
* [**Manthey Corchado, Sergio**](https://github.com/mantheys)
* [**Pérez-Molina, Laura**](https://github.com/LauPM)

![alt text](https://i.imgflip.com/72cpdl.jpg)
