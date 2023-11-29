📚 **LIBRARIES**
=================


io_functions
-------------
.. .. automodule:: lib.io_functions
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. admonition:: **General formatting**

   These functions are used to format the output of the code, for the moment they are helping us to print colored lines in the output to detect errors or warnings.

.. autoclass:: lib.io_functions.print_colored

.. admonition:: **Input/Output files**
   
   These functions are used to read and write files. The input files are stored in the `input` folder as `.txt` files (`read_input_file`). Once the deconvolution is performed, there are new input files generated that can be used to re-run the analysis workflow using the deconvolved waveforms (`list_to_string` + `generate_input_file`). In some functions we need to save some results in a file, for example the results of the calibration/charge fit. The output files are stored in the `fit_data` folder as `.txt` files using `write_output_file` function:

.. autoclass:: lib.io_functions.read_input_file
.. autoclass:: lib.io_functions.list_to_string
.. autoclass:: lib.io_functions.generate_input_file
.. autoclass:: lib.io_functions.write_output_file


.. admonition:: **Raw data to npy/npz files**

   These functions are used to convert the raw(`.root` or `.dat`) data files to `.npy` or `.npz` files. For example, with raw data stored as `run00/wave0.dat` after running `binary2npy` we will create a folder `run00_ch0` where we will store the `.npy` files and each `.npy` file will be have the name of the variable we are storing (i.e `ADC.npy`, `AveWvf.npy`, `PedSTD.npy`, `Sampling.npy`).

.. autoclass:: lib.io_functions.binary2npy
.. autoclass:: lib.io_functions.root2npy

.. admonition:: **Dictionaries's Keys**
   
   These functions are used to check, print and delete the keys of a dictionary. The keys are the names of the variables stored in the dictionary that correspond to the names of the `.npy` files stored before.

.. autoclass:: lib.io_functions.check_key
.. autoclass:: lib.io_functions.print_keys
.. autoclass:: lib.io_functions.delete_keys

.. admonition:: **Load/Save npy/npz files**
   
   These functions are used to load and save the `.npy` files. Firstly, we have a function used to get the list of preset names that we want to load or save. This output list is used then in the `load/save` functions.

.. autoclass:: lib.io_functions.get_preset_list
.. autoclass:: lib.io_functions.load_npy
.. autoclass:: lib.io_functions.save_proccesed_variables

---------------------------------------------------------------------------------------------------------------------------------------------

head_functions module
--------------------------

These functions are used to start the macros, configure the flags and information provided by the user.

.. automodule:: lib.head_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


ana_functions
-------------
.. .. automodule:: lib.ana_functions
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. admonition:: **General analysis**
   
   These functions are used to perform general analysis of the data. For example, we can use the `insert_variable` function to insert a new variable in the dictionary. The `generate_cut_array` function is used to generate the cut array that we will use to select the events that we want to analyze. The `get_units` function is used to get the units of the variables stored in the dictionary.

.. autoclass:: lib.ana_functions.insert_variable
.. autoclass:: lib.ana_functions.generate_cut_array
.. autoclass:: lib.ana_functions.get_units

.. admonition:: **Computing peak/pedestal variables**
   
   These functions are used to compute the peak and pedestal varibales of the raw waveforms (`compute_peak_variables`, `compute_pedestal_variables`, `compute_pedestal_variables_sliding_window`, `compute_pedestal_sliding_windows`). We can also compute the processed waveforms with the pedestal subtracted as well as computing the power spectrum of the waveforms (`compute_ana_wvfs`, `compute_power_spec`). Finally, we are trying to optimize the functions by introducing `numba` libraries. The `shift_ADCs` function is used to shift the ADCs of the waveforms to the pedestal value. The `shift4_numba` function is used to shift the ADCs of the waveforms to the pedestal value using `numba` library.

.. autoclass:: lib.ana_functions.compute_peak_variables
.. autoclass:: lib.ana_functions.compute_pedestal_variables
.. autoclass:: lib.ana_functions.compute_ana_wvfs
.. autoclass:: lib.ana_functions.compute_power_spec

---------------------------------------------------------------------------------------------------------------------------------------------

wvf_functions
-------------
.. .. automodule:: lib.wvf_functions
..    :members:
..    :undoc-members:
..    :show-inheritance:

These are more specific functions for analysing the waveforms. 

.. admonition:: **Average Waveforms**
   
   The following functions compute the average waveforms of the processed individual events.

.. autoclass:: lib.wvf_functions.average_wvfs
.. autoclass:: lib.wvf_functions.expo_average
.. autoclass:: lib.wvf_functions.unweighted_average
.. autoclass:: lib.wvf_functions.smooth

.. admonition:: **Integration**
   
   Then we can use these average waveform reference values to choose an integration (or other criteria) to get the pC and PE.

.. autoclass:: lib.wvf_functions.find_baseline_cuts
.. autoclass:: lib.wvf_functions.find_amp_decrease
.. autoclass:: lib.wvf_functions.integrate_wvfs

---------------------------------------------------------------------------------------------------------------------------------------------

vis_functions
-------------
.. .. automodule:: lib.vis_functions
..    :members:
..    :undoc-members:
..    :show-inheritance:

These functions are used to visualize the data.

.. admonition:: **Individual Events and Waveforms**
   
   Individual events of a run prnting important parameters. We can compare them with the computed Average Waveform is computed and also we can plot several average waveforms in the same plot.

.. autoclass:: lib.vis_functions.vis_npy
.. autoclass:: lib.vis_functions.vis_compare_wvf

.. admonition:: **Histograms**

   1D and 2D histograms of the chosen variables (in principle these histograms are used to generate cuts of outlying events).

.. autoclass:: lib.vis_functions.vis_var_hist
.. autoclass:: lib.vis_functions.vis_two_var_hist

Finally we can print the statistics of the variables stored in the dictionary.
.. autoclass:: lib.vis_functions.print_stats

---------------------------------------------------------------------------------------------------------------------------------------------

cal_functions
-------------

.. automodule:: lib.cal_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

dec_functions
-------------

.. automodule:: lib.dec_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

cut_functions
-------------

.. automodule:: lib.cut_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

fit_functions
-------------

.. automodule:: lib.fit_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

fig_config module
----------------------

.. automodule:: lib.fig_config
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

ply_functions module
-------------------------

.. automodule:: lib.ply_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------

sim_functions module
-------------------------

.. automodule:: lib.sim_functions
   :members:
   :undoc-members:
   :show-inheritance: