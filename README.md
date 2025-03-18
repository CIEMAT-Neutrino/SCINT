# SCINT (Sensor Calibration Interface for Neutrino Team)

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Documentation Status](https://readthedocs.org/projects/scint/badge/?version=latest)](https://scint.readthedocs.io/en/latest/?badge=latest)
[![DockerPulls](https://img.shields.io/docker/pulls/neutrinosciemat/scint)](https://hub.docker.com/r/neutrinosciemat/scint)

This is a Python library to process and analyze raw data from the lab (waveform per waveform mode).

### :book: Access the [DOCUMENTATION](https://scint.readthedocs.io/en/latest/) for more information 


### 0 Download

Clone the repository into a local directory and create your branch:

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

### 1 To start RUN:

Set all the utilities needed for the macros:
  
```bash
source setup.sh
source .venv/bin/activate
```

### 2 Run the following macros FROM the macros' folder:

```bash
cd srcs/macros
python3 XXmacro.py (--flags input) 
```

## CONTRIBUTING

:construction: Work in progress (check [TO DO LIST](https://github.com/orgs/CIEMAT-Neutrino/projects/4)) :construction:

* Make sure you create your `branch` or fork the repository for commiting your changes.
* The branch should tell something about the development you are carring out.
* Once you are sure your development is ready to be shared with the group open a pull request and merge to the main.
* Follow [pep-8](https://peps.python.org/pep-0008/) style Python code ([Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) extension in VSCode will do the formatting for you)
* **Document the code as you go!** (Work in progress to homogenize style in the functions' doc)
    - [Sphinx docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) - [VSCode Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)

    ```bash
    """[Summary]

    :param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
    :type [ParamName]: [ParamType](, optional)
    
    :raises [ErrorType]: [ErrorDescription]

    :return: [ReturnDescription]
    :rtype: [ReturnType]
    """
    ```
* We adopted a formatting style for functions, variables and so on:
    ```bash
    FUNCTIONS & ARGUMENTS → PYTHON NOTATION: low_case + “_” binding (i.e my_runs) 
    KEYS → C++ notation
    SPECIAL DICTIONARIES
        OPT: visualization Options + CHECK KEY
    ```



## LICENSE
[MIT](https://choosealicense.com/licenses/mit/)

## Authors (alphabetical order, please insert your name here if you contribute to this project)

* [**Alvárez-Garrote, Rodrigo**](https://github.com/rodralva)
* [**de la Torre Rojo, Andrés**](https://github.com/andtorre)
* [**Manthey Corchado, Sergio**](https://github.com/mantheys)
* [**Pérez-Molina, Laura**](https://github.com/LauPM)
