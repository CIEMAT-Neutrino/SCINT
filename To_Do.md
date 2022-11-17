1) Histogram visualizer
    - Solve bin number / width ...
3) Add cuts to visualizer 
  3) Variables to cut:
      - Amplitude (min,max)
      - Pedestal max amp > value (look at the histogram amp to check pedestal width)
      - Pedestal STD (think about it...)
      - Peak Time (min, max)
      - Charge (min, max)
      - Two variables cuts (Peak time pro...)
4) Add cuts to functions: average, histograms...
5) ¿Crear funcion de cortes (minmax, corte simultáneo) y añadir un booleano a cada waveform
6) Las funciones cogeran las waveforms en función de los booleanos.
7) Elegir nombres (en general) que tengan sentido y añadir unidades por cada variable calculada (para los ejes de los plots y demás)
8) Añadir unidades a los npy y solucionar lo de los labels
