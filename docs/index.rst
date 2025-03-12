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

.. image:: _static/minions.png
   :width: 500
   :align: center
   :alt: Image of four minions going happily to code


`Rodrigo Álvarez-Garrote <https://github.com/rodralva>`_, `Andrés de la Torre Rojo <https://github.com/andtorre>`_, `Sergio Manthey Corchado <https://github.com/mantheys>`_, `Laura Pérez-Molina <https://github.com/LauPM>`_

The **Sensor Calibration Interface for Neutrino Team** (:tealstext:`SCINT`) is a python library to analyze experimental data acquired by the Neutrino Group.

You can navigate through the documentation using the table of contents below, and you can search for specific keywords using the search tab placed at left side.

---------------------------------------------------------------------------------------------------------------------------------------------

**CONTENTS**
============
.. toctree::   
    :maxdepth: 1

    Intro
    Utils
    Macros
    Libraries
    Everywhere

    examples/examples

---------------------------------------------------------------------------------------------------------------------------------------------

.. warning::
    🚧 This project is still under development. Please, contact the authors for more information.🚧



**SUMMARY**
-------------

For a quick summary or just as a reminder follow the next steps:

You need to have ``git``, ``python (>=3.7)`` and ``pip3`` installed.

1. Make sure you have access to data to analyze:

* **[RECOMENDED] Configure VSCode SSH conection** and work from ``gaeuidc1.ciemat.es`` (you will have access to the data in ``/pc/choozdsk01/DATA/SCINT/folders``)
* Run the usual command to connect via SSH through the terminal: ``ssh AFS_USER@gaeuidc1.ciemat.es``

2. Clone the repository into a local directory and create your branch:

   .. code-block:: bash

      git clone https://github.com/CIEMAT-Neutrino/SCINT.git 
      cd SCINT
      git checkout -b <your_branch_name>

3.  Install packages needed for the library to run ⚠️ **TIME CONSUMING STEP - JUST FIRST TIME** ⚠️:

.. code-block:: bash
   
   source setup.sh

It will ask for confirmation to make sure you are running from ``SCINT`` folder and to link the ``data`` folder with data to run in the tutorial mode. 

4. To run the macros:

   .. code-block:: bash

      cd srcs/macros
      python3 XXmacro.py (--flags input)

If you want to have a personal folder to store your test files locally you can create a ``scratch`` folder (it won't be synchronized with the repository).
Otherwise, you can create a folder for your custom scripts and add them to the ``.gitignore`` file:

.. code-block:: bash

   mkdir <your_folder_name>
   echo "<your_folder_name/*>" >> .gitignore

.. admonition:: **Preferred work-flow**

   * Store raw data in some share space, for example:
      - ``/pc/choozdsk01/DATA/SCINT/your_folder/raw/*`` 
      - ``/pnfs/ciemat.es/neutrinos/LAB/your_folder/raw/*`` ---> used for backup but not during the analysis
   
   * Save the processed data in the generated folder when running ``00Raw2Np.py`` (``.../your_folder/npy/*``)
   
   * Whenever you are done, compress the needed files for the analysis and store them in ``pnfs`` (it would be helpful for the group to include a ``README`` file)

---------------------------------------------------------------------------------------------------------------------------------------------

**INDICES AND TABLES**
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`