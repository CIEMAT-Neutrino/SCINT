==============================
Noise runs visualization
==============================

Here we show an example on how to plot the average waveform of a noise run. You can have a look at the `Noise.py` macro and `Noise.ipynb` notebook for more details.

.. plotly::
      
      import plotly.express
      plotly.io.read_json('vis_noise.json')