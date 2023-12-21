#================================================================================================================================================#
# This library contains functions to perform cut to the data.                                                                                    #
#================================================================================================================================================#

import numpy             as np
import matplotlib.pyplot as plt
import pandas            as pd
from itertools                import product
from scipy.signal             import find_peaks
from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon
from rich                     import print as print


# Import from other libraries
from .io_functions  import print_colored, check_key
from .ana_functions import generate_cut_array, get_units
from .vis_functions import vis_two_var_hist
from .fig_config    import figure_features

def cut_selector(my_runs, user_input, debug=False):
    label = ""
    cut_dict={}
    if user_input["filter"]["cut_df"][0]:
        label = "cut_df_"
        for ldx,cut_list in enumerate(user_input["filter"]["cut_df"][1]):
            this_cut = user_input["filter"]["cut_df"][1][ldx]
            cut_dict[(this_cut[1],this_cut[2],this_cut[3],this_cut[4],ldx)] = this_cut[0]
        cut_df(my_runs, cut_dict=cut_dict, debug=user_input["debug"])
    
    if user_input["filter"]["cut_lin_rel"][0]: 
        label = "cut_lin_rel_"
        cut_lin_rel(my_runs, user_input["filter"]["cut_lin_rel"][1])
    
    if user_input["filter"]["cut_peak_finder"][0]:
        label = "cut_peak_finder_"
        cut_peak_finder(my_runs, user_input["filter"]["cut_peak_finder"][1], user_input["filter"]["cut_peak_finder"][2], debug=user_input["debug"])
    
    return label, my_runs

def print_cut_info(my_cuts, stage="partial", debug=False):
    if stage == "partial": print_colored("Nº selected/total events for this cut: %i/%i (%0.2f"%(np.sum(my_cuts), len(my_cuts), np.sum(my_cuts)/len(my_cuts)*100)+ "%)", color="INFO")
    if stage == "final":   print_colored("Nº selected/total events in total cut: %i/%i (%0.2f"%(np.sum(my_cuts), len(my_cuts), np.sum(my_cuts)/len(my_cuts)*100)+ "%)", color="SUCCESS")

def cut_df(my_runs, cut_dict={}, debug=False):
    '''
    This function cuts the data using a dictionary with the cuts. The dictionary must be in the following format:
    cut_dict = {(key, logic, value, inclusive): channels}
    '''
    print_colored("---- LET'S CUT! ----", color = "SUCCESS",styles=["bold"])
    for run in (np.asarray(my_runs["NRun"]).astype(str)):
        my_cuts = np.ones(len(my_runs[run][my_runs["NChannel"][0]]["TimeStamp"]),dtype=bool)
        my_runs_df = pd.DataFrame(my_runs[run]).T
        for cut in cut_dict:
            this_cut_cut_array = np.ones(len(my_runs[run][my_runs["NChannel"][0]]["TimeStamp"]),dtype=bool)
            channels = cut_dict[cut]; key = cut[0]; logic = cut[1]; value = cut[2]; inclusive = cut[3]
            for ch_idx,ch in enumerate(np.asarray(channels).astype(str)):
                this_channel_cut_array = np.ones(len(my_runs[run][my_runs["NChannel"][0]]["TimeStamp"]),dtype=bool)
                try: my_runs[run][ch]
                except KeyError: print("ERROR: Run",run,"or Ch",ch,"not found in loaded data"); exit()

                if check_key(my_runs[run][ch], "MyCuts") == False:    generate_cut_array(my_runs, debug=debug)
                if check_key(my_runs[run][ch], "UnitsDict") == False: get_units(my_runs, debug=debug)
                print_colored("... Cutting events for run %i channel %i with %s %s %0.2f ..."%(run, ch, key, logic, value),"INFO")
                if logic == "bigger":  this_channel_cut_array = (my_runs_df.loc[ch][key] >  value); print_cut_info(this_channel_cut_array)
                if logic == "smaller": this_channel_cut_array = (my_runs_df.loc[ch][key] <  value); print_cut_info(this_channel_cut_array)
                if logic == "equal":   this_channel_cut_array = (my_runs_df.loc[ch][key] == value); print_cut_info(this_channel_cut_array)
                if logic == "unequal": this_channel_cut_array = (my_runs_df.loc[ch][key] != value); print_cut_info(this_channel_cut_array)

                if ch_idx != 0:
                    if inclusive: this_cut_cut_array = this_cut_cut_array + this_channel_cut_array
                    else:         this_cut_cut_array = this_cut_cut_array * this_channel_cut_array
                    print_colored("\nInclusive = %s"%inclusive,"magenta")
                else:
                    this_cut_cut_array = this_channel_cut_array  
                
            my_cuts = my_cuts * this_cut_cut_array
            print_cut_info(my_cuts, stage="final")
            
        for loaded_ch in my_runs["NChannel"]: my_runs[run][loaded_ch]["MyCuts"] = my_cuts
    print_colored("---- DONE CUT! ----\n", color = "SUCCESS",styles=["bold"])

def cut_min_max(my_runs, keys, limits, ranges = [0,0], chs_cut = [], apply_all_chs = False, debug = False):
    """
    \nThis is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    \n**VARIABLES:**
    \n- keys: a LIST of variables you want to constrain
    \n- limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    \n- ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    \n- chs_cut: a LIST with the affected channels.
    \n- apply_all_chs: a BOOL to decide if we want to reject each cut event for ALL loaded channels.
    \nImportant! Each key works independently. If one key gives True and the other False, it remains False.
    \nExample: keys = ["PeakAmp", "PeakTime"], limits = {"PeakAmp": [20,50], "PeakTime": [4e-6, 5e-6]}
    """

    print_colored("---- LET'S CUT! ----", color = "SUCCESS",styles=["bold"])
    if chs_cut == []: chs_cut = my_runs["NChannel"]
    idx_list = []
    initial_evts = 0
    for run, ch, key in product(my_runs["NRun"], chs_cut, keys):
        if check_key(my_runs[run][ch], "MyCuts") == False:    generate_cut_array(my_runs); print("...Running generate_cut_array...")
        if check_key(my_runs[run][ch], "UnitsDict") == False: get_units(my_runs)

        initial_evts = len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True])
        if run != my_runs["NRun"][0] and ch == chs_cut[0] and key == keys[0]: idx_list = []; print_colored("... NEW RUN ...", color = "WARNING")
        print("--- CUTTING events with ",end ="")
        print_colored(key, color = "cyan" ,end = "");print(" in ("+str(limits[key][0])+", "+str(limits[key][1])+")",my_runs[run][ch]["UnitsDict"][key], "for Ch", ch, "Run",run," ---")
        print("Nº events before cut: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        if check_key(my_runs[run][ch], key) == True:
            rep_idx = 0
            ch_idx_list = 0
            if ranges[0]==0 and ranges[1]==0:
                for i in range(len(my_runs[run][ch][key])):
                    if key == "PeakTime" and (limits[key][0] <= my_runs[run][ch]["Sampling"]*my_runs[run][ch][key][i] <= limits[key][1]): continue
                    elif limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]:                                                    continue
                    else: 
                        if apply_all_chs == False: my_runs[run][ch]["MyCuts"][i] = False
                        else: 
                            if i not in idx_list and my_runs[run][ch]["MyCuts"][i] != False: idx_list.append(i); ch_idx_list = ch_idx_list + 1
                            else:                                                            rep_idx = rep_idx + 1
            else:
                i_idx = int(np.round(ranges[0]/my_runs[run][ch]["Sampling"])); f_idx = int(np.round(ranges[1]/my_runs[run][ch]["Sampling"]))
                for i in range(i_idx,f_idx+1):
                    if limits[key][0] <= my_runs[run][ch][key][i] <= limits[key][1]: continue
                    else: my_runs[run][ch]["MyCuts"][i] = False
            if apply_all_chs == False:
                print("Nº cutted events:", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))
                print("Nº final evts after cutting in",key,"for Ch "+str(ch)+":", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]),"\n")
            else: print("Nº cutted events in Ch "+str(ch)+":",rep_idx+ch_idx_list,"("+str(ch_idx_list),"new events cutted)\n")

        if apply_all_chs == True and ch == chs_cut[-1] and key == keys[-1]:
            print("--- CUTTING EVENTS for ALL (loaded) Chs in Run",run,"---")
            print("Nº of new cutted events in Chs "+str(my_runs["NChannel"])+":", len(idx_list))
            for ch in my_runs["NChannel"]:
                if check_key(my_runs[run][ch], "MyCuts") == False:
                    print("...Running generate_cut_array...\n")
                    generate_cut_array(my_runs)
                for i in idx_list: my_runs[run][ch]["MyCuts"][i] = False
            
            print("Nº total final events in ALL Chs:", initial_evts - len(idx_list),"\n")
    if debug == True: print("... Cuts finished ...")

def cut_ped_std(my_runs, n_std = 2, chs_cut = [], apply_all_chs = False, debug=False):
    '''
    \nThis is a fuction for a cut in the PedSTD. It uses the median as reference and eliminates events with
    \nPedSTD > median + n_std*std, where std is the Standard Deviation of the PedSTD distribution (previously filtered
    \nwith percentiles). 
    \n**VARIABLES:**
    \n- keys: a LIST of variables you want to constrain
    \n- limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    \n- ranges: a LIST with the range where we want to check the key value. If [0,0] it uses the whole window. Time in sec.
    \n- chs_cut: a LIST with the affected channels.
    \n- apply_all_chs: a BOOL to decide if we want to reject each cut event for ALL loaded channels.
    '''

    print_colored("---- LET'S CUT! ----", color = "SUCCESS",styles=["bold"])
    if chs_cut == []: chs_cut = my_runs["NChannel"]
    idx_list = []
    initial_evts = 0
    for run, ch in product(my_runs["NRun"], chs_cut):
        if check_key(my_runs[run][ch], "MyCuts") == False: generate_cut_array(my_runs)
        print("...Running generate_cut_array...\n")

        initial_evts = len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True])
        if run != my_runs["NRun"][0] and ch == chs_cut[0]: idx_list = []; print_colored("... NEW RUN ...", color = "WARNING")

        data = my_runs[run][ch]["PedSTD"]
        ypbot = np.percentile(data, 0.1); yptop = np.percentile(data, 99.9)
        ypad = 0.2*(yptop - ypbot)
        ymin = ypbot - ypad; ymax = yptop + ypad
        data = [i for i in data if ymin<i<ymax]

        # moda = stat.mode(data)
        mediana = np.median(data)
        std = np.std(data)
        print("--- CUTTING events with ", end = "");print_colored("PedSTD",color="cyan",end = "");print(" <",str(n_std)+"* std (of the distribution) for Ch", ch, "Run",run," ---")
        print("Nº events before cut: ", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]))
        ch_idx_list = 0
        rep_idx = 0
        for i in range(len(my_runs[run][ch]["PedSTD"])):
            if mediana + n_std*std > my_runs[run][ch]["PedSTD"][i]: continue    
            else: 
                if apply_all_chs == False: my_runs[run][ch]["MyCuts"][i] = False
                else: 
                    if i not in idx_list and my_runs[run][ch]["MyCuts"][i] != False: idx_list.append(i); ch_idx_list = ch_idx_list + 1
                    else:                                                            rep_idx = rep_idx + 1

        if apply_all_chs == False:
                print("Nº cutted events:", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == False]))
                print("Nº final evts after cutting in PedSTD for Ch "+str(ch)+":", len(my_runs[run][ch]["MyCuts"][my_runs[run][ch]["MyCuts"] == True]),"\n")
        else: print("Nº cutted events in Ch "+str(ch)+":",rep_idx+ch_idx_list,"("+str(ch_idx_list),"new events cutted)\n")

        if apply_all_chs == True and ch == chs_cut[-1]:
            print("--- CUTTING EVENTS for ALL (loaded) Chs ---")
            print("Nº of new cutted events in Chs "+str(my_runs["NChannel"])+":", len(idx_list))
            for ch in my_runs["NChannel"]:
                if check_key(my_runs[run][ch], "MyCuts") == False:
                    print("...Running generate_cut_array...")
                    generate_cut_array(my_runs)
                for i in idx_list: my_runs[run][ch]["MyCuts"][i] = False
            
            print("Nº total final events in ALL Chs:", initial_evts - len(idx_list),"\n")

def cut_lin_rel(my_runs, keys, compare = "NONE", percentile = [0.1,99.9]):
    '''
    \nThis is a function to cut manually with a polygonal figure on two variables. You can do any polygonal figure (avoid strange figures with crossed lines).
    \n"Left click" chooses vertexes, "right click" deletes the last vertex and "middle click" finishes the figure.
    \n**VARIABLES:**
    \n- keys: a LIST of variables you want to plot and cut
    \n- compare: NONE, RUNS, CHANNELS to decide the histogram to use
    \n- percentile: the percentile used to reject outliers in the histogram
    '''

    print_colored("---- LET'S CUT! ----", color = "cyan",styles=["bold"])
    counter = 0
    fig, ax = vis_two_var_hist(my_runs, keys, compare, percentile, OPT = {"SHOW": False})
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            print("...Running generate_cut_array...")
            generate_cut_array(my_runs)

        for j in range(len(keys)):
            if check_key(my_runs[run][ch], keys[j]) == True: continue
            else: print_colored("IAAA ERROR", "ERROR");      break

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
        

def cut_peak_finder(my_runs, number_peaks, wdth = 4, prom = 0.01, dist = 30):
    """
    \nThis is a peak finder (aprox) and cuts events with more than "number_peaks" in the window. It checks if AveWvfSPE exists (for calibration runes)
    \nand set the threshold in 3/4 of the SPE max. Other way it takes into account the Max value in Pedestal (this works well for laser runes).
    \nWARNING! Maybe the values of width, prominence and distance may be changed.
    """
    
    print_colored("---- LET'S CUT! ----", color = "cyan",styles=["bold"])
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

def cut_min_max_sim(my_runs, keys, limits, debug = False):
    '''
    \nThis is a fuction for cuts of min - max values. It takes a variable(s) and checks whether its value is between the specified limits.
    \n**VARIABLES:**
    \n- keys: a LIST of variables you want to constrain at the same time
    \n- limits: a DICTIONARY with same keys than variable "keys" and a list of the min and max values you want.
    \nImportant! Keys are related, so all keys must be False to cut the event. If any of the conditions is True, the event is not cutted.
    \nExample: keys = ["PeakAmp"], limits = {"PeakAmp": [20,50]}
    '''

    print_colored("---- LET'S CUT! ----", color = "cyan",styles=["bold"])
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False: generate_cut_array(my_runs); print("...Running generate_cut_array...")
            
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
    if debug == True: print_colored("---- END OF CUTS ----", color = "cyan",styles=["bold"])