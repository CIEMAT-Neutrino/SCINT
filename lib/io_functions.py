import os, gc
import matplotlib.pyplot as plt
import numpy as np
import uproot
import copy
import stat
from itertools import product
import gc

def color_list(color):
    colors = {
              "DEBUG":   '\033[35m', #PURPLE
              "ERROR":   '\033[91m', #RED
              "SUCCESS": '\033[92m', #GREEN
              "WARNING": '\033[93m', #YELLOW
              "blue":    '\033[94m',
              "magenta": '\033[95m',
              "cyan":    '\033[96m',
              "white":   '\033[97m',
              "black":   '\033[98m',
              "end":     '\033[0m'
              }
    
    return colors[color]

def print_colored(string, color, bold=False, end = "\n"):
    '''
    Print a string in a specific color.
    '''  
    
    color = color_list(color)
    if bold == False: output = color + str(string) + color_list("end")
    if bold == True:  output = '\033[1m' + color + string + color_list("end")
    
    print(output, end = end)

#===========================================================================#
#************************** INPUT FILE *************************************#
#===========================================================================#
def list_to_string(input_list):
    '''
    Convert a list to a string to be written in a .txt file
    '''

    string = str(input_list).replace("[","") 
    string = string.replace("]","") 
    string = string.replace("'","") 
    string = string.replace(" ","") 

    return string 

def generate_input_file(input_file,info,path="../input/",label="",debug=False):
    '''
    Generate a .txt file with the information needed to load the runs and channels.
    '''

    file = open(path+label+str(input_file)+".txt", 'w+')
    for branch in info:
        if branch == "LOAD_PRESET":
            if label == "Gauss" or label == "Wiener":
                info[branch][3] = "DEC"; file.write(branch+": "+list_to_string(info[branch])+"\n")
        elif branch == "REF":
            if label == "Gauss" or label == "Wiener": 
                info[branch][0] = label+"AveWvf"; file.write(branch+": "+list_to_string(info[branch])+"\n")
        elif branch == "LIGHT_RUNS" or branch == "CALIB_RUNS" or branch == "MUON_RUNS":    
            if label == "Gauss" or label == "Wiener": 
                info[branch] = []; file.write(branch+": "+list_to_string(info[branch])+"\n")
        else:
            file.write(branch+": "+list_to_string(info[branch])+"\n")

def read_input_file(input, path = "../input/", debug = False):
    '''
    Obtain the information stored in a .txt input file to load the runs and channels needed.
    '''

    # Using readlines()
    file  = open(path+input+".txt", 'r')
    lines = file.readlines()
    info = dict()
    NUMBERS = ["BITS","DYNAMIC_RANGE","MUONS_RUNS","LIGHT_RUNS","ALPHA_RUNS","CALIB_RUNS","NOISE_RUNS","CHAN_TOTAL","CHAN_POLAR","CHAN_AMPLI"]
    DOUBLES = ["SAMPLING","I_RANGE","F_RANGE"]
    STRINGS = ["DAQ","MODEL","PATH","MONTH","RAW_DATA","OV_LABEL","CHAN_LABEL","LOAD_PRESET","SAVE_PRESET","TYPE","REF"]
    
    # Strips the newline character
    for line in lines:
        for LABEL in DOUBLES: 
            if line.startswith(LABEL):
                info[LABEL] = []; numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                for i in numbers.split(","):
                    try:   info[LABEL].append(float(i)) # Try to convert to float and append to LABEL list
                    except ValueError: 
                        if debug == True: print_colored("Error when reading: " + str(info[LABEL]), "ERROR")
                    if debug: print_colored(str(info[LABEL]), "DEBUG")

        for LABEL in NUMBERS:
            if line.startswith(LABEL):
                info[LABEL] = []; numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                for i in numbers.split(","):
                    try:   info[LABEL].append(int(i)) # Try to convert to int and append to LABEL list
                    except ValueError:
                        if debug == True: print_colored("Error when reading: " + str(info[LABEL]), "ERROR")
                    if debug: print_colored(str(info[LABEL]), "DEBUG")

        for LABEL in STRINGS:
            if line.startswith(LABEL):
                info[LABEL] = []; numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                for i in numbers.split(","):
                    try:   info[LABEL].append(i) # Try to append the string to LABEL list
                    except ValueError:
                        if debug == True: print_colored("Error when reading: " + str(info[LABEL]), "ERROR")
                    
                    if debug: print_colored(str(info[LABEL]), "DEBUG")
    print("\n")
    print(info.keys())
    print("\n")

    return info

def write_output_file(run, ch, output, filename, info, header_list, extra_tab=[], not_saved=[1], path = "../fit_data/"):
    '''
    General function to write a txt file with the outputs obtained.
    \n The file name is defined by the given "filename" variable + _chX. 
    \n If the file existed previously it appends the new fit values (it save the run for each introduced row)
    \n By default we dont save the height of the fitted gaussian in the txt.
    '''
    
    fitted_peaks = len(output)
    par_list = list(range(len(output[0])))
    for p in not_saved:
            par_list.remove(p) #removing parameters before saving in txt (height by default)


    confirmation = input(color_list("magenta")+"\nConfirmation to save in"+path+filename+"_ch%i.txt the printed parameters (except HEIGHT) (y/n) ?"%ch+color_list("end"))
    if "y" in confirmation:
        print("\n----------- Saving -----------")

        if not os.path.exists(path+filename+"_ch%i.txt"%ch): #HEADER#
            os.makedirs(name=path,exist_ok=True) # Create the directory if it doesnt exist
            with open(path+filename+"_ch%i.txt"%ch, 'a+') as f:  f.write("\t".join(header_list)+"\n") # Write the header

        with open(path+filename+"_ch%i.txt"%ch, 'a+') as f:
            for i in np.arange(fitted_peaks):
                if fitted_peaks != 1: aux_label = str(i)+"\t"
                if fitted_peaks == 1: aux_label = ""
                f.write(str(int(run))+"\t"+info["OV_LABEL"][0]+"\t"+aux_label) #OVLABEL no funciona bien
                for k in par_list[:len(par_list)-1]: #save all the parameter list except last element to include \n after it
                    if any (k == t for t in extra_tab): # if k == 3: # for calibration format
                        f.write("\t")
                    f.write(str(output[i][k][0]) +"\t" + str(output[i][k][1])+"\t")
                f.write(str(output[i][-1][0]) +"\t" + str(output[i][-1][1])+"\n")

#===========================================================================#
#************************* RAW TO NUMPY ************************************#
#===========================================================================#

### DEPRECATED --- UPDATE ###
def root2npy(runs, channels, info={}, debug=False): ### ACTUALIZAR COMO LA DE BINARIO ###
    '''
    Dumper from .root format to npy tuples. 
    Input are root input file path and npy outputfile as strings. 
    \n Depends on uproot, awkward and numpy. 
    \n Size increases x2 times. 
    '''

    in_path  = info["PATH"][0]+info["MONTH"][0]+"/raw/"
    out_path = info["PATH"][0]+info["MONTH"][0]+"/npy/"
    for run, ch in product (runs.astype(int),channels.astype(int)):
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file  = "run"+str(run).zfill(2)+"_ch"+str(ch)+".root" # Name of the input file
        out_file = "run"+str(run).zfill(2)+"_ch"+str(ch)+".npy"  # Name of the output file
        
        try:
            my_dict = {}; f = uproot.open(in_path+in_file) # Open the file and dump it in a dictionary
            
            if debug:
                print_colored("----------------------", "DEBUG")
                print_colored("Dumping file:"+str(in_path+in_file), "DEBUG")
            
            for branch in f["IR02"].keys():
                if debug: print_colored("dumping brach:"+str(branch), "DEBUG")
                my_dict[branch]=f["IR02"][branch].array().to_numpy()
            
            # additional useful info
            my_dict["RawADC"] = my_dict["ADC"]
            del my_dict["ADC"]
            my_dict["NBinsWvf"]    = my_dict["RawADC"][0].shape[0]
            my_dict["Sampling"]    = info["SAMPLING"][0]
            my_dict["Label"]       = info["CHAN_LABEL"][j]
            my_dict["RawPChannel"] = int(info["CHAN_POLAR"][j])

            np.save(out_path+out_file,my_dict)
            
            if debug:
                print_colored(my_dict.keys(), "DEBUG")
                print_colored("Saved data in:" +str(out_path+out_file), "DEBUG")
                print_colored("----------------------\n", "DEBUG")

        except FileNotFoundError: print("--- File %s was not foud!!! \n"%in_file)

def binary2npy(runs, channels, info={}, debug=True, compressed=True, header_lines=6, force=False):
    '''
    Dumper from binary format to npy tuples. 
    Input are binary input file path and npy outputfile as strings. 
    \n Depends numpy. 
    '''

    in_path  = info["PATH"][0]+info["MONTH"][0]+"/raw/"
    out_path = info["PATH"][0]+info["MONTH"][0]+"/npy/"
    os.makedirs(name=out_path,exist_ok=True)
    for run, ch in product(runs.astype(int),channels.astype(int)):
        print("\n....... READING RUN%i CH%i ......."%(run, ch))
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file = "run"+str(run).zfill(2)+"/wave"+str(ch)+".dat" # Name of the input file
        out_folder = "run"+str(run).zfill(2)+"_ch"+str(ch)+"/"   # Name of the output folder

        try:
            os.mkdir(out_path+out_folder)
            os.chmod(out_path+out_folder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        except FileExistsError: print_colored("DATA STRUCTURE ALREADY EXISTS", "WARNING") 
        try:
            headers    = np.fromfile(in_path+in_file, dtype='I') # Reading .dat file as uint32
            header     = headers[:6]                             # Read first event header
            
            NSamples   = int(header[0]/2-header_lines*2)         # Number of samples per event (as uint16)
            Event_size = header_lines*2+NSamples                 # Number of uint16 per event
            data       = np.fromfile(in_path+in_file, dtype='H') # Reading .dat file as uint16
            N_Events   = int(data.shape[0]/Event_size)           # Number of events in the file

            #reshape everything, delete unused header
            ADC        = np.reshape(data,(N_Events,Event_size))[:,header_lines*2:]              # Data reshaped as (N_Events,NSamples)
            headers    = np.reshape(headers,(N_Events , int(Event_size/2) )  )[:,:header_lines] # Headers reshaped as (N_Events,header_lines)
            TIMESTAMP  = (headers[:,4]*2**32+headers[:,5]) * 8e-9                               # Unidades TriggerTimeStamp(PC_Units) * 8e-9
                
            branches   = ["RawADC","TimeStamp","NBinsWvf", "Sampling", "Label", "RawPChannel"]                                 # Branches to be saved
            content    = [ADC,TIMESTAMP, ADC.shape[0], info["SAMPLING"][0], info["CHAN_LABEL"][j], int(info["CHAN_POLAR"][j])] # Content to be saved
            files      = os.listdir(out_path+out_folder)                                                                       # List of files in the output folder

            if debug:
                print_colored("#####################################################################","DEBUG")
                print_colored("Header:"+str(header),"DEBUG")
                print_colored("Waveform Samples:"+str(NSamples),"DEBUG")
                print_colored("Event_size(wvf+header):"+str(Event_size),"DEBUG")
                print_colored("N_Events:"+str(N_Events),"DEBUG")
                print_colored("Run time: {:.2f}".format((TIMESTAMP[-1]-TIMESTAMP[0])/60) + " min" ,"DEBUG")
                print_colored("Rate: {:.2f}".format(N_Events/(TIMESTAMP[-1]-TIMESTAMP[0])) + " Events/s" ,"DEBUG")
                print_colored("#####################################################################\n","DEBUG")

            for i, branch in enumerate(branches):
                try:
                    # If the file already exists and force is True, overwrite it
                    if (branch+".npz" in files or branch+".npy" in files) and force == True: 
                        print_colored("File (%s.npx) already exists. OVERWRITTEN"%branch, "WARNING")
                        if compressed: # If compressed, save .npz
                            try:   os.remove(out_path+out_folder+branch+".npz") # Remove the file if it already exists (permissions issues)
                            except FileNotFoundError: print_colored(".npy was found but not .npz", "ERROR")  
                            np.savez_compressed(out_path+out_folder+branch+".npz", content[i])                      # Save the file
                            os.chmod(out_path+out_folder+branch+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # Set permissions

                        else: # If not compressed, save .npy
                            try:   os.remove(out_path+out_folder+branch+".npy") # Remove the file if it already exists (permissions issues)
                            except FileNotFoundError: print_colored(".npz was found but not .npy", "ERROR") 
                            np.save(out_path+out_folder+branch+".npy", content[i])                                  # Save the file
                            os.chmod(out_path+out_folder+branch+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # Set permissions
                            
                    # If file already exists, skip
                    elif branch+".npz" in files and force == False: print_colored("File (%s.npz) alredy exists."%branch, "WARNING"); continue 

                    # If file does not exist, save it
                    else: 
                        np.savez_compressed(out_path+out_folder+branch+".npz", content[i])                      # Save the file
                        os.chmod(out_path+out_folder+branch+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # Set permissions

                        if not compressed:
                            np.save(out_path+out_folder+branch+".npy", content[i])                                  # Save the file
                            os.chmod(out_path+out_folder+branch+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # Set permissions

                    if debug:
                        print_colored(branch, "DEBUG")
                        print_colored("Saved data in:"  + str(out_path+out_folder+branch)+".npx", "DEBUG")
                        print_colored("----------------------\n", "DEBUG")
                    gc.collect()

                except FileNotFoundError: print("--- File %s was not foud!!! \n"%in_file)
        except FileNotFoundError: print("--- File %s was not foud!!! \n"%(in_path+in_file))


#===========================================================================#
#***************************** KEYS ****************************************#
#===========================================================================#

def check_key(OPT, key):
    ''' 
    Checks if the given key is included in the dictionary OPT.
    \n Returns a bool. (True if it finds the key)
    '''

    try:   OPT[key]; return True   # If the key is found, return True 
    except KeyError: return False  # If the key is not found, return False

def print_keys(my_runs):
    '''
    Prints the keys of the run_dict which can be accesed with run_dict[runs][channels][BRANCH] 
    '''

    try:
        for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
            print("------------------------------------------------------------------------------------------------------------------------------------------------------")
            print("Dictionary keys --> ",list(my_runs[run][ch].keys()))
            print("------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    except KeyError: print_colored("Empty dictionary. No keys to print.", "ERROR")

def delete_keys(my_runs, keys):
    '''
    Delete the keys list introduced as 2nd variable
    '''

    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        try:   del my_runs[run][ch][key]      # Delete the key
        except KeyError: print_colored("*EXCEPTION: [Run%i - Ch%i - %s] key combination is not found in my_runs"%(run,ch,key), "WARNING")   

def get_preset_list(my_run, path, folder, preset, option, debug = False):
    '''
    Return as output presets lists for load/save npy files.
    VARIABLES:
       \n - my_run: my_runs[run][ch]
       \n - path: saving path
       \n - folder: saving in/out folder
       \n - preset: 
            (a) "ALL": all the existing keys/branches
            (b) "ANA": only Ana keys/branches (removing RAW info)
            (c) "INT": only Charge*, Ave* keys/branches
            (d) "RAW": only Raw information i.e loaded from Raw2Np + Raw* keys
            (e) "EVA": all the existing keys/branches EXCEPT ADC
            (f) "DEC": only DEC info i.e Wiener*, Gauss*, Dec* or Charge* keys
            (g) "CAL": only Charge* keys
       \n - option:
            (a) "LOAD": takes the os.listdir(path+folder) as brach_list (IN)
            (b) "SAVE": takes the my_run.keys() as branch list (OUT)
    '''

    dict_option = dict()
    dict_option["LOAD"] = os.listdir(path+folder)
    dict_option["SAVE"] = my_run.keys()

    if preset == "ALL":  # Save all branches
        branch_list = dict_option[option]
        if "UnitsDict" in branch_list: branch_list.remove("UnitsDict")
        if "MyCuts" in branch_list: branch_list.remove("MyCuts")

    elif preset == "ANA": # Remove Raw, Dict and Cuts branches
        branch_list = dict_option[option]; aux = []
        for key in branch_list:
            if not "Raw" in key and not "Dict" in key and not "Cuts" in key: aux.append(key)
        branch_list = aux

    elif preset == "RAW":  # Save aux + Raw branches
        branch_list = dict_option[option]; aux = ["NBinsWvf", "TimeStamp","Sampling", "Label"]
        for key in branch_list:
            if "Raw" in key: aux.append(key) 
        branch_list = aux

    elif preset == "INT": # Save aux + Charge* and Ave* branches
        branch_list = dict_option[option]; aux = ["NBinsWvf", "TimeStamp", "Sampling", "Label"]
        for key in branch_list:
            if "Charge" in key and key not in aux: aux.append(key)
            if "Ave" in key and key not in aux: aux.append(key)
        branch_list = aux

    elif preset == "EVA": # Remove ADC, Dict and Cuts branches
        branch_list = dict_option[option]
        aux = ["NBinsWvf",  "TimeStamp", "Sampling", "Label"]
        for key in branch_list:
            if not "ADC" in key and not "Dict" in key and not "Cuts" in key: aux.append(key) # and key not in aux # add??
        branch_list = aux

    elif preset == "DEC": # Save aux + Gauss*, Wiener*, Dec* and Charge* branches
        branch_list = dict_option[option]
        aux = ["NBinsWvf",  "TimeStamp", "Sampling", "Label", "SER"]
        for key in branch_list:
            if "Gauss" in key or "Wiener" in key or "Dec" in key or "Charge" in key: aux.append(key) # and key not in aux # add??
        branch_list = aux

    elif preset == "CAL": # Save aux + Charge* branches
        branch_list = dict_option[option]; aux = ["ADC","PedLim","Label","Sampling"]
        for key in branch_list:
            if "Charge" in key and key not in aux: aux.append(key)
        branch_list = aux

    if debug: print_colored("\nPreset branch_list:" + str(branch_list), "DEBUG")
    return branch_list

#===========================================================================#
#************************** LOAD/SAVE NPY **********************************#
#===========================================================================# 

def load_npy(runs, channels, preset="", branch_list = [], info={}, debug = False, compressed=True):
    '''
    Structure: run_dict[runs][channels][BRANCH] 
    \n Loads the selected channels and runs, for simplicity, all runs must have the same number of channels
    \n Presets can be used to only load a subset of desired branches. ALL is default.
    '''

    path = info["PATH"][0]+info["MONTH"][0]+"/npy/"

    my_runs = dict()
    my_runs["NRun"]     = runs
    my_runs["NChannel"] = channels

    for run in runs:
        my_runs[run]=dict()
        for ch in channels:
            my_runs[run][ch]=dict()
            in_folder="run"+str(run).zfill(2)+"_ch"+str(ch)+"/"
            if preset!="": branch_list = get_preset_list(my_runs[run][ch], path, in_folder, preset, "LOAD", debug) # Get the branch list if preset is used
            for branch in branch_list:   
                try:
                    # if "Dict" in branch: #BORRAR A NO SER QUE ALGUNA VEZ QUERAMOS CARGAR ALGUN DICCIONARIO
                    #     my_runs[run][ch][branch.replace(".npz","")] = np.load(path+in_folder+branch.replace(".npz","")+".npz",allow_pickle=True, mmap_mode="w+")["arr_0"].item()   
                    # else:
                    if compressed:
                        my_runs[run][ch][branch.replace(".npz","")] = np.load(path+in_folder+branch.replace(".npz","")+".npz",allow_pickle=True, mmap_mode="w+")["arr_0"]     
                        if branch.__contains__("ADC"):my_runs[run][ch][branch.replace(".npz","")]=my_runs[run][ch][branch.replace(".npz","")].astype(float)
                    else:
                        my_runs[run][ch][branch.replace(".npy","")] = np.load(path+in_folder+branch.replace(".npy","")+".npy",allow_pickle=True, mmap_mode="w+").item()
                        if branch.__contains__("ADC"):my_runs[run][ch][branch.replace(".npy","")]=my_runs[run][ch][branch.replace(".npy","")].astype(float)

                    if debug: print_colored("\nLoaded %s run with keys:"%branch + str(my_runs.keys()), "DEBUG")
                    if debug: print_colored("-----------------------------------------------", "DEBUG")
                except FileNotFoundError: print_colored("\nRun %i, channels %i --> NOT LOADED (FileNotFound)"%(run,ch), "ERROR")
            print_colored("load_npy --> DONE!\n", "SUCCESS")
            del branch_list # Delete the branch list to avoid loading the same branches again
    return my_runs

def save_proccesed_variables(my_runs, preset = "", branch_list = [], info={}, force=False, debug = False, compressed=True):
    '''
    Saves the processed variables an npx file.
    VARIABLES:
    \n - my_runs: dictionary with the runs and channels to be saved
    \n - preset: preset to be used to save the variables
    \n - branch_list: list of branches to be saved
    \n - info: dictionary with the path and month to be used
    \n - force: if True, the files will be overwritten
    \n - debug: if True, the function will print the branches that are being saved
    \n - compressed: if True, the files will be saved as npz, if False, as npy
    '''

    aux = copy.deepcopy(my_runs) # Save a copy of my_runs with all modifications and remove the unwanted branches in the copy
    path = info["PATH"][0]+info["MONTH"][0]+"/npy/"
    # opath = info["OPATH"][0]+info["MONTH"][0]+"/npy/"

    for run in aux["NRun"]:
        for ch in aux["NChannel"]:
            out_folder = "run"+str(run).zfill(2)+"_ch"+str(ch)+"/"
            os.makedirs(name=path+out_folder,exist_ok=True)
            files=os.listdir(path+out_folder)
            if not branch_list: branch_list = get_preset_list(my_runs[run][ch],path, out_folder, preset, "SAVE", debug)
            print(branch_list)
            for key in branch_list:
                key = key.replace(".npz","")

                # If the file already exists, skip it
                if key+".npz" in files and force == False: print("File (%s.npz) alredy exists"%key); continue 
                
                # If the file already exists and force is True, overwrite it
                elif (key+".npz" in files or key+".npy" in files) and force == True:        
                    if compressed:
                        print_colored("File (%s.npz) OVERWRITTEN "%key, "WARNING")
                        os.remove(path+out_folder+key+".npz")
                        np.savez_compressed(path+out_folder+key+".npz",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    else:
                        print_colored("File (%s.npy) OVERWRITTEN "%key, "WARNING")
                        os.remove(path+out_folder+key+".npy")
                        np.save(path+out_folder+key+".npy",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                
                # If the file does not exist, create it
                else: 
                    print_colored("Saving NEW file: %s.npz"%key, "SUCCESS")
                    print(path+out_folder+key+".npz")
                    np.savez_compressed(path+out_folder+key+".npz",aux[run][ch][key])
                    os.chmod(path+out_folder+key+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

                    if not compressed:
                        print_colored("Saving NEW file: %s.npy"%key, "SUCCESS")
                        np.save(path+out_folder+key+".npy",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    del my_runs 
    
#DEPREACTED??#
def copy_single_run(my_runs, runs, channels, keys):
    my_run = dict()
    my_run["NRun"] = []
    my_run["NChannel"] = []
    for run, ch, key in product(runs,channels,keys):
        try:
            my_run["NRun"].append(run)
            my_run["NChannel"].append(ch)
            my_run[run] = dict()
            my_run[run][ch] = dict()
            my_run[run][ch][key] = my_runs[run][ch][key]
        except KeyError: print_colored(str(run) + str(ch)  +str(key) + " key combination is not found in my_runs", "ERROR")
    return my_run
