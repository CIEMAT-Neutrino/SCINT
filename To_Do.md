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

------ CYTHON WORKSHOP II ------

- [ ] QUITAR BUCLES (cambiar for por vectores)
    - [ ] Problema con el procesado de WFS: procesarlas run a run i.e hacer una macro que ejecute python3 ... para cada run y no pete
    - [ ] El resto sin bucle (poner un WARNING?)
    - [ ] INDEXADO para quitar los bucles en los cortes
- [ ] Añadir al ppio de las funciones una comprobacion de si existen cortes generados y aplicarlos en las funciones que vengan despues. No queremos guardar una branch con los cortes
- [ ] Comprobar ganancias FEB22_2 (testear que los resultados son compatibles con las otras macros)
- [ ] TESTS para las medidas XA-SBND 
- [ ] Imports desde un .py comun
- [ ] No pasar por los .root :)
- [ ] Cambiar estructura a carpeta (run00_ch00) con .npy (Ana/Dec/Fit) que serian las ramas del root + info extra que vamos añadiendo. Hay que cambiar os prefijos para que sean el nombre de los .npy. Puedes cargas las ramas que elijas. Kind of solve memory problem
- [ ] Libreria de fit: no saca el chi2; hay que cambiarla o ver como añadirlo
persistencia no funciona
- [ ] HANDS-ON

EXTRAS PARA CUANDO TODO FUNCIONE BIEN
- [ ] Cabeceras {ADC, Osciloscopio}
- [ ] Segmentados binarios del osciloscopio a npy
- [ ] Cambiar sampling – por characteristics del setup (sampling, ganancia electrónica, bits adc, etc)


------ CYTHON WORKSHOP I ------

- [x] ~~NOMBRES variables/funciones~~
    - FUNCIONES Y ARGUMENTOS → PYTHON NOTATION
      my_runs: low_case + “_” binding
    - KEYS → C++ notation
    - SPECIAL DICTIONARIES
        - OPT: visualization Options + CHECK KEY
        - CUT: cortes
- [x] ~~Documentar funciones~~
- [x] ~~Cortes~~
- [x] ~~Visualizador~~
- [x] ~~Check merge main (dictadura)  → script rutina para check nada roto~~
- [x] ~~Lectura datos + binario → meter antiguas macros~~
- [x] ~~Lectura datos ¿nueva forma sin pasar por .root?~~
- [x] ~~Load cargue la siguiente run si encuentra alguna que no existe~~
- [x] ~~txt de entrada con las runes para no modificar las runes~~
- [ ] Colores comunes (DUNE plot-style¿?)

------ CYTHON WORKSHOP 0 ------

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