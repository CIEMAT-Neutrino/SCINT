.. SCINT documentation master file, created by
   sphinx-quickstart on Fri Jun 23 17:36:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. raw:: html

   <style> 
      .tealtitle {color:#008080; font-weight:bold; font-size:60px} 
      .tealsttle {color:#008080; font-weight:bold; font-size:30px} 
      .tealstext {color:#008080; font-weight:bold; font-size:17px} 
      .tealtexts {color:#008080; font-weight:bold; font-size:12px} 
   </style>

.. role:: tealtitle
.. role:: tealsttle
.. role:: tealstext
.. role:: tealtexts


====================================================
            :tealtitle:`WELCOME TO SCINT !!`
====================================================

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠴⠚⠛⠓⠶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣤⣄⣀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⢀⣠⣴⡶⣆⠀⠀⠀⠀⠀⣠⣴⣶⣿⣦⣄⠀⠀⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠻⣿⡏⠀⡞⣩⣍⡽⠤⢤⡿⣧⡀⢸⣿⣾⠃⠀⣰⣿⠿⠃⣰⣿⣷⠴⠤⣄⡀⣿⣥⣿⡉⣿⣿⡿⠶⢶⣦⣾⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⠋⠉⣫⡽⢿⣶⠦⣀⠀
⠀⠀⠀⢹⡇⠈⠳⣿⡏⢴⣢⣾⣇⠀⢻⣄⠈⢿⡆⠀⠙⢷⣶⣿⣿⣿⣿⣦⡀⠀⠹⡎⠙⡟⠻⠛⠉⠀⠀⠀⠀⡇⠐⣷⣶⡆⠀⠀⠀⠀⠻⣧⣴⣞⠋⠁⣠⣿⡄⠈⡇
⠀⠀⠀⡴⢿⡦⣄⠀⠙⠿⠿⠻⣿⣆⠀⠙⣦⠈⢿⡄⠀⠈⠛⠉⠉⠁⠈⠙⢿⣦⡀⢹⢸⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠙⠛⢿⣦⡀⢀⣔⣀⣀⣀⠈⠛⠿⠟⠛⢿⣦⠁
⠀⢀⣾⣷⣽⠿⠿⠇⠀⠀⠀⠀⠈⠻⣷⡀⠈⣇⣸⢻⣿⣿⡦⠀⠀⠀⠀⠀⠀⠹⣷⣀⡎⠠⠤⠤⠖⠛⠀⠀⢀⡇⠀⠀⠀⠀⠙⢻⠏⠘⣷⣶⣯⣽⡦⠀⠀⠀⠀⣻⠇
⠀⣼⣷⣿⣿⣿⣦⣄⡀⠀⠀⠀⠀⠀⠘⢿⣄⣹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⢸⣀⡀⠀⠀⠀⠀⣀⣠⣾⠀⠀⠀⠀⠀⠀⠘⣧⠀⠈⠉⠙⠋⠁⠀⠀⣀⡴⠋⠀
⢰⡟⢻⣿⣧⣾⣿⠋⠙⠛⠳⢶⣤⣀⠀⢈⣿⣿⣷⣮⣹⣿⡶⠖⠛⠛⠛⠳⣾⡅⠀⣼⢻⣿⣿⣿⡿⠛⠉⠉⣘⣧⣄⠀⠀⠀⠀⣸⠝⣳⣶⣤⣤⣴⡿⠿⠛⢿⡁⠀⠀
⢸⣷⣾⡟⢻⣿⣇⠀⠀⠀⠀⠀⠈⠛⢿⠋⢹⣿⣯⣿⣿⣿⡁⠀⠀⠀⢠⣞⣥⡇⢰⣿⣿⣿⣿⠻⣧⣤⣀⣠⡏⠉⢛⣇⠀⠀⢸⣿⣾⣿⣿⣯⣿⡇⠀⠀⣴⣿⣿⡇⠀
⣈⠻⣏⣰⣾⡻⣿⣿⣶⣤⣄⣀⣠⠞⢹⠀⠀⠻⣿⣿⣶⣿⣿⣿⣷⣶⡿⢿⡿⠁⠈⢿⣿⣿⣿⣧⡹⣿⣿⣿⠃⠀⣹⣿⡀⠀⠘⢿⣿⣿⣿⣿⣿⣷⣶⣶⡿⠛⠋⠁⠀
⠻⢿⣿⡿⠛⠛⠛⢻⣿⣿⡿⠛⢻⣿⡿⠀⢲⣾⣿⣿⠋⠉⣿⣿⡟⠉⠀⠀⠀⠀⠸⢿⣿⣿⠁⠙⣿⣿⠉⠁⠀⠀⠙⠿⠃⠘⢷⣾⣿⡿⠉⠉⠙⢿⣿⡏⠀⠀⠀⠀⠀
⠀⠀⠈⠀⠀⠀⠀⠉⠉⠉⠁⠀⠈⠉⠁⠀⠀⠈⠉⠋⠀⠀⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠈⠉⠀⠀⠀

`Rodrigo Álvarez-Garrote <https://github.com/rodralva>`_, `Andrés de la Torre Rojo <https://github.com/andtorre>`_, `Sergio Manthey Corchado <https://github.com/mantheys>`_, `Laura Pérez-Molina <https://github.com/LauPM>`_

The **Sensor Calibration Interface for Neutrino Team** (:tealstext:`SCINT`) is a python library to analyze experimental data acquired by the Neutrino Group.

You can navigate through the documentation using the table of contents below and you can search for specific keywords using the search tab placed at left side.

---------------------------------------------------------------------------------------------------------------------------------------------

**CONTENTS**
============
.. toctree::   
    :maxdepth: 1

    Intro  
    Utils  
    Macros  
    Libraries
    EveryWhere

    examples/examples

---------------------------------------------------------------------------------------------------------------------------------------------

.. warning::
    🚧 This project is still under development. (You may find some references to :tealstext:`CYTHON TOOLS` our previous library) 
    Please, contact the authors for more information.🚧



**SUMMARY**
-------------

For a quick summary or just as a reminder follow the next steps:

You need to have ``git``, ``python (>=3.7)`` and ``pip3`` installed.

0.- Clone the repository into a local directory and create your branch:

.. code-block:: bash

   git clone https://github.com/CIEMAT-Neutrino/SCINT.git 
   cd SCINT
   git checkout -b <your_branch_name>


1.- Install packages needed for the library to run:

* **[RECOMENDED] Work with VSCode**:
   - Install VSCode and some extensions: Remote-SSH, Jupyter, vscode-numpy-viewer, **Python Environment Manager**
   - CREATE VIRTUAL ENVIRONMENT: **VSCode venv extension**. It will recommend you the ``/scripts/requirements.txt`` packages and it will automatically install them :)
   
* From CIEMAT computers
      - CREATE VIRTUAL ENVIRONMENT: 

        .. code-block:: bash

            mkdir venv_python3.7
            cd venv_python3.7
            /cvmfs/sft.cern.ch/lcg/releases/Python/3.7.3-f4f57/x86_64-centos7-gcc7-opt/bin/python3 -m venv .
            source bin/activate

2.- Prepare the library to be run (just the first time):

.. code-block:: bash

   cd SCINT/scripts
   sh setup.sh

To be run from the ``scripts`` folder (it will ask you for confirmation) and it will download the ``notebooks`` folder to make your analysis. 
Additionally, if you have created your own virtual environment in a CIEMAT computer you need to install some packages (make sure it is activated) and answer ``y`` to the INSTALL question. If have created the virtual enviroment with the VSCode extension you will have them installed already, answer ``n``.

3.- Make sure you have access to data to analyze:

* **[RECOMMENDED] Configure VSCode SSH connection** and work from ``gaeuidc1.ciemat.es`` (you will have access to the data in ``/pc/choozdsk01/palomare/SCINT/folders``)
* Mount the folder with the data in your local machine ``sshfs pcaeXYZ:/pc/choozdsk01/palomare/SCINT/folder ../data`` making sure you have an empty ``data`` folder 📂.
* Copy the data to your local machine. See ``sh scripts/copy_data.sh`` for an example on how to copy the ``TUTORIAL`` data

4.- Have a look on the ``notebooks`` folder to see how to visualize data and run the macros:

.. code-block:: bash

   cd ../notebooks
   juptyer notebook 00TUTORIAL.ipynb

This folder is prepared **NOT** to be synchronized with the repository so you can make your own analysis without affecting the rest of the team.
If you think your analysis can be useful for the rest of the team contact the authors to add it to the repository.

If you want to have a personal folder to store your test files locally you can create an ``scratch`` folder (it won't be synchronized with the repository).
Otherwise you can create a folder for your custom scripts and add them to the ``.gitignore`` file:

.. code-block:: bash

   mkdir <your_folder_name>
   echo "<your_folder_name/*>" >> .gitignore


5.- To run the macros:

.. code-block:: bash

   cd ../macros
   python3 XXmacro.py (--flags input)


.. admonition:: **Preferred work-flow**

   * Store raw data in some share space, for example:
      - ``/pc/choozdsk01/palomare/SCINT/your_folder/raw/*`` 
      - ``/pnfs/ciemat.es/neutrinos/your_folder/raw/*`` [slower]
   
   * Save the processed data in the generated folder when running ``00Raw2Np.py`` (``.../your_folder/npy/*``)
   
   * Whenever you are done, compress the needed files for the analysis and store them in ``pnfs`` (it would be helpful to include a ``README`` file)

---------------------------------------------------------------------------------------------------------------------------------------------

**INDICES AND TABLES**
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`