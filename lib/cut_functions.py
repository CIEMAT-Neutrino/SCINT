import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from itertools import product
from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

from .io_functions  import check_key,print_keys,copy_single_run, print_colored
from .vis_functions import vis_two_var_hist
from .ana_functions import generate_cut_array
from .fit_functions import gaussian,loggaussian,gaussian_train,loggaussian_train
from .fig_config    import*


def cut_min_max(my_runs, keys, limits, ranges = [0,0]):
    '''
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
       \n - keys: a LIST of variables you want to constrain
       \n - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
       \n - ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    Important! Each key works independently. If one key gives True and the other False, it remains False.
    Example: keys = ["PeakAmp", "PeakTime"], limits = {"PeakAmp": [20,50], "PeakTime": [4e-6, 5e-6]}
    '''

    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)
        
        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        if check_key(my_runs[run][ch], key) == True:
            if ranges[0]==0 and ranges[1]==0:
                for i in range(len(my_runs[run][ch][key])):
                    if key == "PeakTime" and limits[key][0] <= my_runs[run][ch]["Sampling"]*my_runs[run][ch][key][i] <= limits[key][1]:
                        continue
                    elif limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]:
                        continue
                    else: my_runs[run][ch]["MyCuts"][i] = False
            else:
                i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                for i in range(i_idx,f_idx+1):
                    if limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]:
                        continue
                    else: my_runs[run][ch]["MyCuts"][i] = False
            print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))
        print("Nº total final events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))

def cut_min_max_sim(my_runs, keys, limits):
    '''
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
       \n - keys: a LIST of variables you want to constrain at the same time
       \n - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    Important! Keys are related, so all keys must be False to cut the event. If any of the conditions is True, the event is not cutted.
    Example: keys = ["PeakAmp"], limits = {"PeakAmp": [20,50]}
    '''

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        for i in range(len(my_runs[run][ch][keys[0]])):
            for j in range(len(keys)):
                if check_key(my_runs[run][ch], keys[j]) == True:
                    if limits[keys[j]][0] <= my_runs[run][ch][keys[j]][i] <= limits[keys[j]][1]:
                        my_runs[run][ch]["MyCuts"][i] = True
                        break
                    else: my_runs[run][ch]["MyCuts"][i] = False
                else: print(keys," does not exist in my_runs!")
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))

def cut_lin_rel(my_runs, keys):
    '''
    This is a function to cut manually with a polygonal figure on two variables. You can do any polygonal figure (avoid strange figures with crossed lines).
    "Left click" chooses vertexes, "right click" deletes the last vertex and "middle click" finishes the figure.
    VARIABLES:
       \n - keys: a LIST of variables you want to plot and cut
    '''

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        for j in range(len(keys)):
            if check_key(my_runs[run][ch], keys[j]) == True: continue
            else: print_colored("IAAA ERROR", "ERROR");      break

        figure_features()
        fig, ax = vis_two_var_hist(my_runs,run,ch,[keys[0],keys[1]], [0.1,99.9], OPT = {"Show": False})
        coords = fig.ginput(100, timeout=1000)
        polygon = Polygon(coords)
        n_points = len(coords)
        print("Nº points: ", n_points)
        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        
        x_coords = []; y_coords = []; 
        for k in range(n_points): x_coords.append(coords[k][0])
        for k in range(n_points): y_coords.append(coords[k][1])
        m_values = []; n_values = []
        for i in range(n_points):
            if i == n_points-1:
                delta_y = y_coords[0] - y_coords[i]; delta_x = x_coords[0] - x_coords[i]
                m_values.append(delta_y / delta_x)
                n_values.append(y_coords[i] - m_values[i] * x_coords[i])
                x_aux = np.linspace(x_coords[i], x_coords[0], 500); y_aux = x_aux*m_values[i] + n_values[i]
                ax.plot(x_aux, y_aux, "k--", alpha = 0.6)
            else:
                delta_y = y_coords[i+1] - y_coords[i]; delta_x = x_coords[i+1] - x_coords[i]
                m_values.append(delta_y / delta_x)
                n_values.append(y_coords[i] - m_values[i] * x_coords[i])
                x_aux = np.linspace(x_coords[i], x_coords[i+1], 500); y_aux = x_aux*m_values[i] + n_values[i]
                ax.plot(x_aux, y_aux, "k--", alpha = 0.6)
        for i in range(len(my_runs[run][ch][keys[0]])):
            point = Point(my_runs[run][ch][keys[0]][i], my_runs[run][ch][keys[1]][i])
            if  polygon.contains(point): my_runs[run][ch]["MyCuts"][i] = True
            else: my_runs[run][ch]["MyCuts"][i] = False
        
        ax.scatter(my_runs[run][ch][keys[0]][my_runs[run][ch]["MyCuts"] == False],my_runs[run][ch][keys[1]][my_runs[run][ch]["MyCuts"] == False], c = "red", s = 2)
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"])-
                  len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        
        while not fig.waitforbuttonpress(-1): pass

def cut_ped_std(my_runs):
    '''
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
       \n - keys: a LIST of variables you want to constrain
       \n - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
       \n - ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    Important! Each key works independently. If one key gives True and the other False, it remains False.
    Example: keys = ["PeakAmp", "PeakTime"], limits = {"PeakAmp": [20,50], "PeakTime": [4e-6, 5e-6]}
    '''

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)
        
        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        print(np.std(my_runs[run][ch]["PedMean"]))
        
        for i in range(len(my_runs[run][ch]["PedSTD"])):
            if np.std(my_runs[run][ch]["PedMean"]) > my_runs[run][ch]["PedRMS"][i]: continue    
            else: my_runs[run][ch]["MyCuts"][i] = False
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))