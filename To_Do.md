## OBJETIVOS
- [ ] Estudiar detector
    - [ ] Ganancia → Calibración → {CORTES + AJUSTES GAUSSIANOS}
    - [ ] Análisis de datos (procesado RAW)
    - [ ] Caracterización → Fits efectivos, X-talk

- [ ] Estudios física
    - [ ] Deconvolución de señales
    - [ ] Fits de física
    - [ ] Simulaciones MC

- [ ] Estudios electrónica


## CYTHON TO DO LIST (NEW)
- [ ] Memoria
- [x] NOMBRES variables/funciones
    - FUNCIONES Y ARGUMENTOS → PYTHON NOTATION
      my_runs: low_case + “_” binding
    - KEYS → C++ notation
    - SPECIAL DICTIONARIES
        - OPT: visualization Options + CHECK KEY
        - CUT: cortes
- [x] Documentar funciones
- [x] Cortes
- [x] Visualizador
- [x] Check merge main (dictadura)  → script rutina para check nada roto
- [x] Lectura datos + binario → meter antiguas macros 
- [ ] Lectura datos ¿nueva forma sin pasar por .root?
- [ ] Estructura fija. Separar cositas
- [ ] Colores comunes
- [x] Load cargue la siguiente run si encuentra alguna que no existe
- [x] txt de entrada con las runes para no modificar las runes
- [ ] Chequear si las variables se sobreescriben bien
- [ ] librerías (Sergio?)
- [ ] mejorar (Sergio?)
- [ ] Estructura de diccionarios CAMBIAR¿? 

------ old ------

- [ ] Histogram visualizer
    - Solve bin number / width ...
- [ ] Add cuts to visualizer 
    - [ ] Variables to cut:
      - Amplitude (min,max)
      - Pedestal max amp > value (look at the histogram amp to check pedestal width)
      - Pedestal STD (think about it...)
      - Peak Time (min, max)
      - Charge (min, max)
      - Two variables cuts (Peak time pro...)
- [ ] Add cuts to functions: average, histograms...
- [ ] ¿Crear funcion de cortes (minmax, corte simultáneo) y añadir un booleano a cada waveform
- [ ] Las funciones cogeran las waveforms en función de los booleanos.
- [ ] Elegir nombres (en general) que tengan sentido y añadir unidades por cada variable calculada (para los ejes de los plots y demás)
- [ ] Añadir unidades a los npy y solucionar lo de los labels




