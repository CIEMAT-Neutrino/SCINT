import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from itertools import product
from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

from .io_functions  import check_key,print_keys,copy_single_run
from .vis_functions import vis_two_var_hist
from .ana_functions import generate_cut_array, get_units
from .fit_functions import gaussian,loggaussian,gaussian_train,loggaussian_train
from .fig_config    import*
from scipy.signal import find_peaks


def cut_min_max(my_runs, keys, limits, ranges = [0,0], chs_cut = [], apply_all_chs = False):
    """
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
        - keys: a LIST of variables you want to constrain
        - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
        - ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    Important! Each key works independently. If one key gives True and the other False, it remains False.
    Example: keys = ["PeakAmp", "PeakTime"], limits = {"PeakAmp": [20,50], "PeakTime": [4e-6, 5e-6]}
    """
    if chs_cut == []: chs_cut = my_runs["NChannel"]
    idx_list = []
    initial_evts = 0
    for run, ch, key in product(my_runs["NRun"], chs_cut, keys):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)
        if check_key(my_runs[run][ch], "UnitsDict") == False:
                get_units(my_runs)
        initial_evts = len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True])
        print("--- CUTTING EVENTS with", key ,"in ("+str(limits[key][0])+", "+str(limits[key][1])+")",my_runs[run][ch]["UnitsDict"][key], "for Ch", ch, " ---")
        print("Nº events before cut: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        if check_key(my_runs[run][ch], key) == True:
            ch_idx_list = 0
            rep_idx = 0
            if ranges[0]==0 and ranges[1]==0:
                for i in range(len(my_runs[run][ch][key])):
                    if key == "PeakTime" and (limits[key][0] <= my_runs[run][ch]["Sampling"]*my_runs[run][ch][key][i] <= limits[key][1]):
                        continue
                    elif limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]:
                        continue
                    else: 
                        if apply_all_chs == False: my_runs[run][ch]["MyCuts"][i] = False
                        else: 
                            if i not in idx_list and my_runs[run][ch]["MyCuts"][i] != False: idx_list.append(i); ch_idx_list = ch_idx_list + 1
                            else: rep_idx = rep_idx + 1
            else:
                i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                for i in range(i_idx,f_idx+1):
                    if limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]:
                        continue
                    else: my_runs[run][ch]["MyCuts"][i] = False
            if apply_all_chs == False:
                print("Nº cutted events:", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))
                print("Nº final evts after cutting in",key,"for Ch "+str(ch)+":", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]),"\n")
            else:
                print("Nº cutted events in Ch "+str(ch)+":",rep_idx+ch_idx_list,"("+str(ch_idx_list),"new events cutted)\n")

    if apply_all_chs == True:
        print("--- CUTTING EVENTS for ALL (loaded) Chs ---")
        print("Nº of new cutted events in Chs "+str(chs_cut)+":", len(idx_list))
        for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
            if check_key(my_runs[run][ch], "MyCuts") == False:
                print("...Running generate_cut_array...")
                generate_cut_array(my_runs)
            for i in idx_list:
                my_runs[run][ch]["MyCuts"][i] = False
        print("Nº total final events in ALL Chs:", initial_evts - len(idx_list),"\n")


def cut_min_max_sim(my_runs, keys, limits):
    """
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
        - keys: a LIST of variables you want to constrain at the same time
        - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    Important! Keys are related, so all keys must be False to cut the event. If any of the conditions is True, the event is not cutted.
    Example: keys = ["PeakAmp"], limits = {"PeakAmp": [20,50]}
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        print("--- CUTTING EVENTS ---")
        for i in range(len(my_runs[run][ch][keys[0]])):
            for j in range(len(keys)):
                if check_key(my_runs[run][ch], keys[j]) == True:
                    if limits[keys[j]][0] <= my_runs[run][ch][keys[j]][i] <= limits[keys[j]][1]:
                        my_runs[run][ch]["MyCuts"][i] = True
                        print("Key", keys[j], "number ",j,"Evt ",i," Break aquí")
                        break
                    else: 
                        my_runs[run][ch]["MyCuts"][i] = False
                        print("Key", keys[j], "number ",j,"Evt ",i," Cut aquí")
                else: print(keys," does not exist in my_runs!")
                print("Final result is", my_runs[run][ch]["MyCuts"][i])
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))

def cut_lin_rel(my_runs, keys, compare = "NONE", percentile = [0.1,99.9]):
    """
    This is a function to cut manually with a polygonal figure on two variables. You can do any polygonal figure (avoid strange figures with crossed lines).
    "Left click" chooses vertexes, "right click" deletes the last vertex and "middle click" finishes the figure.
    VARIABLES:
        - keys: a LIST of variables you want to plot and cut
    """
    counter = 0
    fig, ax = vis_two_var_hist(my_runs, keys, compare, percentile, OPT = {"SHOW": False})
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        for j in range(len(keys)):
            if check_key(my_runs[run][ch], keys[j]) == True:
                continue
            else: print("IAAA ERROR"); break

        figure_features()
        evts_cut = 0
        idx_list = []
        print("--- CUTTING EVENTS MANUALLY USING A POLYGON ---")
        plt.ion()
        coords = fig[counter].ginput(100, timeout=1000)
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
                ax[counter].plot(x_aux, y_aux, "k--", alpha = 0.6)
            else:
                delta_y = y_coords[i+1] - y_coords[i]; delta_x = x_coords[i+1] - x_coords[i]
                m_values.append(delta_y / delta_x)
                n_values.append(y_coords[i] - m_values[i] * x_coords[i])
                x_aux = np.linspace(x_coords[i], x_coords[i+1], 500); y_aux = x_aux*m_values[i] + n_values[i]
                ax[counter].plot(x_aux, y_aux, "k--", alpha = 0.6)
        for i in range(len(my_runs[run][ch][keys[0]])):
            point = Point(my_runs[run][ch][keys[0]][i], my_runs[run][ch][keys[1]][i])
            if my_runs[run][ch]["MyCuts"][i] != False:
                if  polygon.contains(point): my_runs[run][ch]["MyCuts"][i] = True
                else: 
                    my_runs[run][ch]["MyCuts"][i] = False
                    idx_list.append(i)
                    evts_cut += 1
        
        ax[counter].scatter(my_runs[run][ch][keys[0]][idx_list],my_runs[run][ch][keys[1]][idx_list], c = "red", s = 1)
        print("Nº cutted events:",evts_cut)
        print("Nº total final events:",len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        while not fig[counter].waitforbuttonpress(-1): pass
        plt.close()
        counter += 1
        

def cut_ped_std(my_runs):
    """
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
        - keys: a LIST of variables you want to constrain
        - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
        - ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    Important! Each key works independently. If one key gives True and the other False, it remains False.
    Example: keys = ["PeakAmp", "PeakTime"], limits = {"PeakAmp": [20,50], "PeakTime": [4e-6, 5e-6]}
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)
        
        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        print(np.std(my_runs[run][ch]["PedMean"]))
        
        for i in range(len(my_runs[run][ch]["PedSTD"])):
            if np.std(my_runs[run][ch]["PedMean"]) > my_runs[run][ch]["PedRMS"][i]:
                continue    
            else: my_runs[run][ch]["MyCuts"][i] = False
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))

def cut_peak_finder(my_runs, keys, number_peaks):
    """
    This is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    VARIABLES:
        - keys: a LIST of variables you want to constrain at the same time
        - limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    Important! Keys are related, so all keys must be False to cut the event. If any of the conditions is True, the event is not cutted.
    Example: keys = ["PeakAmp"], limits = {"PeakAmp": [20,50]}
    """
    wdth = 4
    prom = 0.01
    dist  = 30
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        print("Nº total events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]), "for Run ", run, "Ch ", ch)
        print("---- CUTTING EVENTS with ",number_peaks," or more peaks ----")
        if check_key(my_runs[run][ch], "AveWvfSPE") == True:
                thresh = np.max(my_runs[run][ch]["AveWvfSPE"])*3/4
        for i in range(len(my_runs[run][ch]["ADC"])):
            # These parameters must be modified according to the run...
            if check_key(my_runs[run][ch], "AveWvfSPE") == False:
                thresh = my_runs[run][ch]["PedMax"][i] + 0.5*my_runs[run][ch]["PedMax"][i]
            peak_idx, _ = find_peaks(my_runs[run][ch]["ADC"][i], height = thresh, width = wdth, prominence = prom, distance=dist)
            if number_peaks > len(peak_idx):
                continue
            else: 
                my_runs[run][ch]["MyCuts"][i] = False
        print("Nº cutted events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))
        print("Nº total final events: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
