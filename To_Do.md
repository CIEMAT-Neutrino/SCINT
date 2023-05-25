## CYTHON TO DO LIST

------ CYTHON WORKSHOP III ------
- [ ] Carpeta tutorial sin tocar, cada uno su carpeta de macros en su branch. Para cambios relevantes para todos se cambia tutorial.
- [ ] Notebook visualizador/cortes etc

- [ ] FUSION JOYTHON EN CYTHON --> Andres tiene partes integradas y Rodrigo ha hecho merge de joython en su carpeta
- [ ] NOTEBOOKS: VisEvent, Cortes
- [x] Merge rama de Andres (Sergio?) y 
- [ ] entender los problemas que hemos tenido
- [ ] DOCUMENTACION, OUTPUT POR TERMINAL, WIKI, COLORSTYLE
- [ ] PASAR A DATAFRAME (read from dat could be the same; load in a df directly from the npy; saving new columns etc)
- [ ] HTML PARA VER EN DIRECTO LOS PLOTS DE RUIDO EN LA TOMA DE DATOS
- [ ] EXTRAS
 

------ CYTHON WORKSHOP II ------

- [ ] Las cargas que se calculan de nuevo se sobrescriben tal y como esta ahora mismo. hay que pensar como organizar eso. 
- [x] ~~Falta por implementar que se pueda repetir el fit y le puedas dar valores de entrada por ejemplo (calib/scintill)~~
- [ ] En la de scintillation hay que poner que rango de cargas de los que hay calculados quieres usar/fittear o lo que sea
- [x] ~~El fit del perfil de centelleo para sacar la tau_slow etc~~ --> LISTO EN DECONVOLUCION
- [ ] Calcular NEvents/s ???
- [ ] Documentar algunas cosas que faltan en las funciones + Wiki (hace mas pequeño el codigo o resumir lo importante)
- [ ] Mejorar los output por terminal (~~colores~~)
- [x] ~~(Extra: Calibracion pmt)~~
- [ ] (Extra: Analisis DC)
- [ ] ColorStyle
- [x] ~~Leer TimeStamp --> calcular tiempo medida runs / Rate~~
- [ ] Integrar cada waveform

- [ ] QUITAR BUCLES (cambiar for por vectores)
    - [ ] Problema con el procesado de WFS: procesarlas run a run i.e hacer una macro que ejecute python3 ... para cada run y no pete
    - [ ] El resto sin bucle (poner un WARNING?)
    - [x] ~~INDEXADO para quitar los bucles en los cortes~~ (EJEMPLO TO CHECK: my_run[run][ch][key][my_run[run][ch]["MyCuts"] == True] )
- [x] ~~Añadir al ppio de las funciones una comprobacion de si existen cortes generados y aplicarlos en las funciones que vengan despues.~~
- [x] ~~No queremos guardar una branch con los cortes --> Ahora se esta guardando~~
- [x] ~~Comprobar ganancias FEB22_2 (testear que los resultados son compatibles con las otras macros)~~
- [x] ~~TESTS para las medidas XA-SBND~~
- [x] ~~Imports desde un .py comun~~
- [x] ~~No pasar por los .root :)~~
- [x] ~~Cambiar estructura a carpeta (run00_ch00) con .npy (Ana/Dec/Fit) que serian las ramas del root + info extra que vamos añadiendo. Hay que cambiar os prefijos para que sean el nombre de los .npy. Puedes cargas las ramas que elijas. Kind of solve memory problem~~
- [x] ~~Libreria de fit: no saca el chi2; hay que cambiarla o ver como añadirlo/calcularlo~~

        import numpy as np
        from scipy.optimize import curve_fit
        import matplotlib.pyplot as plt
        def fit_gaussians(x, y, N, p0):
            assert x.shape == y.shape, "Input arrays must have the same shape."
            def gaussian(x, a, x0, sigma):
                return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
            try:
                popt, pcov = curve_fit(lambda x, *p0: np.sum([gaussian(x, p0[j], p0[j+1], p0[j+2]) for j in range(0, len(p0), 3)]), x, y, p0=p0)
                fit_y = np.sum([gaussian(x, popt[j], popt[j+1], popt[j+2]) for j in range(0, len(popt), 3)])
                chi_squared = np.sum((y - fit_y) ** 2 / fit_y) / np.abs(y.size - len(popt))
                plt.plot(x, y, 'b-', label='data')
                plt.plot(x, fit_y, 'r-', label='fit')
                plt.legend()
                plt.show()
                return popt, chi_squared
            except:
                print("Fit failed.")

- [x] ~~persistencia no funciona~~

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
