📚 **LIBRARIES**
=================


**ANA**
-------------


.. admonition:: **SUMMARY**

   Waveforms related functions.

   * **General analysis**. Insert a new variable in the dictionary (`insert_variable`), generate the cut array, get the units of the variables stored in the dictionary.
   * **Peak/pedestal** variables. Compute the peak and pedestal variables of the raw waveforms (`compute_peak_variables`, `compute_pedestal_variables`, `compute_pedestal_variables_sliding_window`, `compute_pedestal_sliding_windows`). We can also compute the processed waveforms with the pedestal subtracted as well as computing the power spectrum of the waveforms (`compute_ana_wvfs`, `compute_power_spec`). Finally, we are trying to optimize the functions by introducing `numba` libraries. The `shift_ADCs` function is used to shift the ADCs of the waveforms to the pedestal value. The `shift4_numba` function is used to shift the ADCs of the waveforms to the pedestal value using `numba` library.
   * **Average waveforms**. The following functions compute the average waveforms of the processed individual events.
   * **Integration**. Then we can use these average waveform reference values to choose an integration (or other criteria) to get the pC and PE.

.. automodule:: lib.ana_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**CAL**
-------------


.. admonition:: **SUMMARY**

   These functions are used to perform calibration.

.. automodule:: lib.cal_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**CUT**
-------------


.. admonition:: **SUMMARY**

   These functions are used to perform cuts.

.. automodule:: lib.cut_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**DEC**
-------------


.. admonition:: **SUMMARY**

   These functions are used to perform deconvolution.

.. automodule:: lib.dec_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**FIG CONFIG**
----------------------


.. automodule:: lib.fig_config
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**FIT**
-------------


.. admonition:: **SUMMARY**

   These functions are used to perform fits.

.. automodule:: lib.fit_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**GROUP**
-------------------------


.. automodule:: lib.group_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**HEAD**
--------------------------


.. admonition:: **SUMMARY**

   These functions are used to start the macros, configure the flags and information provided by the user.

.. automodule:: lib.head_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**IO**
--------------------------


.. admonition:: **SUMMARY**

   * **Read/write**. Input files stored in the `config/input` folder (`read_input_file`). After deconvolution, new input files generated and can be used to re-run the workflow (`list_to_string` + `generate_input_file`). 
   * **Conversion**. From raw(`.root` or `.dat`) data files to `.npy` or `.npz` files. For example, with raw data stored as `run00/wave0.dat` after running `binary2npy` we will create folders `run00/ch0` where we will store the `.npy` files. Each `.npy` file will have the name of the variable we are storing (i.e `ADC.npy`, `AveWvf.npy`, `PedSTD.npy`, `Sampling.npy`).
   * [DEPRECATING] Check and delete the keys of a dictionary. The keys are the names of the variables stored in the dictionary that correspond to the names of the `.npy` files stored before.
   * **Load/save** `.npy` files. Get the list of preset names that we want to load or save. This output list is used then in the `load/save` functions.

.. automodule:: lib.io_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**MINUIT**
-------------


.. admonition:: **SUMMARY**

   These functions are used to perform fits.

.. automodule:: lib.minuit_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**PLY**
-------------------------


.. automodule:: lib.ply_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**SIM**
-------------------------


.. automodule:: lib.sim_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**STY**
-------------------------


.. automodule:: lib.sty_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**UNIT**
-------------------------


.. automodule:: lib.unit_functions
   :members:
   :undoc-members:
   :show-inheritance:

---------------------------------------------------------------------------------------------------------------------------------------------


**VIS**
-------------


.. admonition:: **SUMMARY**

   These functions are used to visualize the data.

   * **Individual evts**.  We can compare them with the computed `AveWaveform` is computed, and also we can plot several average waveforms in the same plot (`vis_npy`, `vis_compare_wvf`).
   * **Histograms**. 1D and 2D histograms of the chosen variables. In principle these histograms are used to generate cuts of outlying events (`vis_var_hist`, `vis_two_var_hist`).
   * **Statistics**. we can print the statistics of the variables stored in the dictionary (`print_stats`).

.. automodule:: lib.vis_functions
   :members:
   :undoc-members:
   :show-inheritance:
