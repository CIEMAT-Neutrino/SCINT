#================================================================================================================================================#
# This library contains general functions used to read/write files, load/save data, etc.                                                         #
#================================================================================================================================================#

import os, gc, uproot, copy, stat
import numpy as np
import pandas as pd
from itertools import product

def color_list(color):
    '''
    \nFunction which returns the color in ascii.
    '''
    colors = {
              "DEBUG":   '\033[35m', #PURPLE
              "ERROR":   '\033[91m', #RED
              "SUCCESS": '\033[92m', #GREEN
              "WARNING": '\033[93m', #YELLOW
              "INFO":    '\033[94m', #BLUE
              "blue":    '\033[94m', #BLUE
              "magenta": '\033[95m',
              "cyan":    '\033[96m',
              "white":   '\033[97m',
              "black":   '\033[98m',
              "end":     '\033[0m'
              }
    
    return colors[color]

def print_colored(string, color, bold=False, end = "\n"):
    '''
    \nPrint a string in a specific color.
    '''  
    
    color = color_list(color)
    if bold == False: output = color + str(string) + color_list("end")
    if bold == True:  output = '\033[1m' + color + string + color_list("end")
    
    print(output, end = end)

def print_dict(dictionary, debug=False):
    '''
    \nPrint the keys and values of a dictionary.
    '''
    
    for key, value in dictionary.items(): print(str(key) + ": " + str(value))

#===========================================================================#
#************************** INPUT FILE *************************************#
#===========================================================================#
def read_input_file(input,NUMBERS=[],DOUBLES=[],STRINGS=[],BOOLEAN=[],path = "../input/",debug = False):
    '''
    \nObtain the information stored in a .txt input file to load the runs and channels needed.
    \n**VARIABLES**:
    \n- input: name of the input file
    \n- path: path to the input file
    \n- debug: if True, print debug messages
    '''
    if debug: print_colored("\nReading input file: "+str(input)+".txt\n", "DEBUG")
    # Using readlines()
    file  = open(path+input+".txt", 'r')
    lines = file.readlines()
    info = dict()
    info["NAME"] = [input]
    if NUMBERS == []: NUMBERS = ["BITS","DYNAMIC_RANGE","MUONS_RUNS","LIGHT_RUNS","ALPHA_RUNS","CALIB_RUNS","NOISE_RUNS","CHAN_TOTAL","CHAN_POLAR","CHAN_AMPLI"]
    if DOUBLES == []: DOUBLES = ["SAMPLING","I_RANGE","F_RANGE"]
    if STRINGS == []: STRINGS = ["DAQ","MODEL","PATH","MONTH","RAW_DATA","OV_LABEL","CHAN_LABEL","LOAD_PRESET","SAVE_PRESET","TYPE","REF","ANA_KEY","PED_KEY"]
    if BOOLEAN == []: BOOLEAN = []
    # Strips the newline character
    for line in lines:
        for LABEL in DOUBLES: 
            if line.startswith(LABEL):
                # if debug: print_colored(line, "DEBUG")
                try:
                    info[LABEL] = []
                    numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                except IndexError:
                    if debug == True: print_colored(str(LABEL)+":\nNo value found!\n", "WARNING")
                    continue

                for i in numbers.split(","):
                    try:   info[LABEL].append(float(i)) # Try to convert to float and append to LABEL list
                    except ValueError: 
                        if debug == True: print_colored("Error when reading: " + str(LABEL), "ERROR")
                if debug: print_colored(str(line)+str(info[LABEL])+"\n", "DEBUG")

        for LABEL in NUMBERS:
            if line.startswith(LABEL):
                # if debug: print_colored(line, "DEBUG")
                try:
                    info[LABEL] = []
                    numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                except IndexError:
                    if debug == True: print_colored(str(LABEL)+":\nNo value found!\n", "WARNING")
                    continue

                for i in numbers.split(","):
                    try:   info[LABEL].append(int(i)) # Try to convert to int and append to LABEL list
                    except ValueError:
                        if debug == True: print_colored("Error when reading: " + str(LABEL), "ERROR")
                if debug: print_colored(str(line)+str(info[LABEL])+"\n", "DEBUG")

        for LABEL in STRINGS:
            if line.startswith(LABEL):
                # if debug: print_colored(line, "DEBUG")
                try:
                    info[LABEL] = []
                    numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                except IndexError:
                    if debug == True: print_colored(str(LABEL)+":\nNo value found!\n", "WARNING")
                    continue

                for i in numbers.split(","):
                    try:   info[LABEL].append(i) # Try to append the string to LABEL list
                    except ValueError:
                        if debug == True: print_colored("Error when reading: " + str(LABEL), "ERROR")
                if debug: print_colored(str(line)+str(info[LABEL])+"\n", "DEBUG")
        for LABEL in BOOLEAN:
            if line.startswith(LABEL):
                # if debug: print_colored(line, "DEBUG")
                try:
                    info[LABEL] = []
                    numbers = line.split(" ")[1].strip("\n") # Takes the second element of the line
                except IndexError:
                    if debug == True: print_colored(str(LABEL)+":\nNo value found!\n", "WARNING")
                    continue

                for i in numbers.split(","):
                    try:   info[LABEL].append(i.lower() in ["yes","y","true","t","si","s"]) # Try to append the string to LABEL list
                    except ValueError:
                        if debug == True: print_colored("Error when reading: " + str(LABEL), "ERROR")
                if debug: print_colored(str(line)+str(info[LABEL])+"\n", "DEBUG")
    return info

def cuts_info2dict(user_input, info, debug=False):
    '''
    \nConvert the information stored in the input file to a dictionary with the cuts information.
    '''
    cuts_dict = {'cut_df': [False, []], 'cut_lin_rel': [False, []], 'cut_peak_finder': [False, []]}
    keep_reading = True
    if debug: print_colored("Reading cuts from input file %s"%info["NAME"][0], "DEBUG")
    for i, cut in enumerate(cuts_dict):
        idx = 0
        while keep_reading:
            try: 
                input_list = [str(idx)+"CUT_CHAN",str(idx)+"CUT_TYPE",str(idx)+"CUT_KEYS",str(idx)+"CUT_LOGIC",str(idx)+"CUT_VALUE",str(idx)+"CUT_INCLUSIVE"]
                info = read_input_file(user_input["input_file"][0], STRINGS = input_list, debug=False)
                cuts_dict[cut][1].append([info[str(idx)+"CUT_CHAN"], info[str(idx)+"CUT_KEYS"][0], info[str(idx)+"CUT_LOGIC"][0], float(info[str(idx)+"CUT_VALUE"][0]), info[str(idx)+"CUT_INCLUSIVE"][0].lower() in ["yes","y","true","t","si","s"]])
                if cuts_dict[cut][0] == False: cuts_dict[cut][0] = True
                idx += 1
                if debug: print_colored("Cuts dictionary: "+str(cuts_dict), "DEBUG")
            except KeyError:
                keep_reading = False
    if debug and idx == 0: print_colored("No cuts imported from input!", "DEBUG")
    return cuts_dict

def list_to_string(input_list):
    '''
    \nConvert a list to a string to be written in a .txt file
    \nUsed in generate_input_file.
    '''

    string = str(input_list).replace("[","") 
    string = string.replace("]","") 
    string = string.replace("'","") 
    string = string.replace(" ","") 

    return string 

def generate_input_file(input_file,info,path="../input/",label="",debug=False):
    '''
    \nGenerate a .txt file with the information needed to load the runs and channels.
    \nUsed when deconvolving signals to be able to re-start the analysis workflow with the deconvolved waveforms.
    '''

    file = open(path+label+str(input_file)+".txt", 'w+')
    for branch in info:
        if branch == "CHAN_POLAR":
            if label == "Gauss" or label == "Wiener": 
                info[branch] = len(info[branch])*[1]
        if branch == "LOAD_PRESET":
            if label == "Gauss" or label == "Wiener":
                info[branch][1] = "DEC"
                info[branch][2] = "DEC"
                info[branch][3] = "DEC"
                info[branch][4] = "DEC"
                file.write(branch+": "+list_to_string(info[branch])+"\n")
        # elif branch == "REF":
        #     if label == "Gauss" or label == "Wiener": 
        #         info[branch][0] = label+"AveWvf"; file.write(branch+": "+list_to_string(info[branch])+"\n")
        # elif branch == "LIGHT_RUNS" or branch == "CALIB_RUNS" or branch == "MUON_RUNS":    
        #     if label == "Gauss" or label == "Wiener": 
        #         info[branch] = []; file.write(branch+": "+list_to_string(info[branch])+"\n")
        elif branch == "ANA_KEY":
            if label == "Gauss" or label == "Wiener": 
                info[branch] = label; file.write(branch+": "+list_to_string(info[branch])+"\n")
        else:
            file.write(branch+": "+list_to_string(info[branch])+"\n")


def write_output_file(run, ch, output, filename, info, header_list, extra_tab=[], not_saved=[1], path = "../data/"):
    '''
    \nGeneral function to write a txt file with the outputs obtained.
    \nThe file name is defined by the given "filename" variable + _chX. 
    \nIf the file existed previously it appends the new fit values (it save the run for each introduced row)
    \nBy default we dont save the height of the fitted gaussian in the txt.
    '''

    # Check if folder exists
    folder_path  = info["MONTH"][0]+"/fit_data/run"+str(run)+"_ch"+str(ch)+"/"
    if not os.path.exists(path+folder_path): os.makedirs(name=path+folder_path,exist_ok=True)
    fitted_peaks = len(output)
    par_list = list(range(len(output[0])))
    for p in not_saved: par_list.remove(p) #removing parameters before saving in txt (height by default)

    confirmation = input(color_list("magenta")+"\nConfirmation to save in"+path+folder_path+filename+"_ch%i.txt the printed parameters (except HEIGHT) (y/n)? "%ch+color_list("end"))
    if "y" in confirmation:
        print("\n----------- Saving -----------")

        if not os.path.exists(path+folder_path+filename+"_ch%i.txt"%ch): #HEADER#
            os.makedirs(name=path+folder_path,exist_ok=True)             # Create the directory if it doesnt exist
            with open(path+folder_path+filename+"_ch%i.txt"%ch, 'a+') as f:  f.write("\t".join(header_list)+"\n") # Write the header

        with open(path+folder_path+filename+"_ch%i.txt"%ch, 'a+') as f:
            for i in np.arange(fitted_peaks):
                if fitted_peaks != 1: aux_label = str(i)+"\t"
                if fitted_peaks == 1: aux_label = ""
                f.write(str(int(run))+"\t"+info["OV_LABEL"][0]+"\t"+aux_label) #OVLABEL no funciona bien
                for k in par_list[:len(par_list)-1]:                           #save all the parameter list except last element to include \n after it
                    if any (k == t for t in extra_tab): f.write("\t")          # if k == 3: # for calibration format
                    f.write(str(output[i][k][0]) +"\t" + str(output[i][k][1])+"\t")
                f.write(str(output[i][-1][0]) +"\t" + str(output[i][-1][1])+"\n")

#===========================================================================#
#************************* RAW TO NUMPY ************************************#
#===========================================================================#
def binary2npy_express(in_file, header_lines=6, debug=False):
    '''
    \nDumper from binary format to npy tuples. 
    \nInput are binary input file path and npy outputfile as strings. 
    \nDepends numpy. 
    '''

    try:    headers = np.fromfile(in_file, dtype='I')               # Reading .dat file as uint32
    except: headers = np.frombuffer(in_file.getbuffer(), dtype='I') # io.UnsupportedOperation: fileno --> when browsing file

    try:    data = np.fromfile(in_file, dtype='H')               # Reading .dat file as uint16
    except: data = np.frombuffer(in_file.getbuffer(), dtype='H') # io.UnsupportedOperation: fileno --> when browsing file
    
    header     = headers[:6]                             # Read first event header
    NSamples   = int(header[0]/2-header_lines*2)         # Number of samples per event (as uint16)
    Event_size = header_lines*2+NSamples                 # Number of uint16 per event
    N_Events   = int(data.shape[0]/Event_size)           # Number of events in the file

    #reshape everything, delete unused header
    ADC        = np.reshape(data,(N_Events,Event_size))[:,header_lines*2:]              # Data reshaped as (N_Events,NSamples)
    headers    = np.reshape(headers,(N_Events , int(Event_size/2) )  )[:,:header_lines] # Headers reshaped as (N_Events,header_lines)
    TIMESTAMP  = (headers[:,4]*2**32+headers[:,5]) * 8e-9                               # Unidades TriggerTimeStamp(PC_Units) * 8e-9
        
    if debug:
        print_colored("#####################################################################","DEBUG")
        print_colored("Header:"+str(header),"DEBUG")
        print_colored("Waveform Samples:"+str(NSamples),"DEBUG")
        print_colored("Event_size(wvf+header):"+str(Event_size),"DEBUG")
        print_colored("N_Events:"+str(N_Events),"DEBUG")
        print_colored("Run time: {:.2f}".format((TIMESTAMP[-1]-TIMESTAMP[0])/60) + " min" ,"DEBUG")
        print_colored("Rate: {:.2f}".format(N_Events/(TIMESTAMP[-1]-TIMESTAMP[0])) + " Events/s" ,"DEBUG")
        print_colored("#####################################################################\n","DEBUG")

    return ADC, TIMESTAMP

def binary2npy(runs, channels, user_input, debug=True, compressed=True, header_lines=6, force=False):
    '''
    \nDumper from binary format to npy tuples. 
    \nInput are binary input file path and npy outputfile as strings. 
    \nDepends numpy. 
    '''
    info = read_input_file(user_input["input_file"][0],debug=user_input["debug"])

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
            ADC, TIMESTAMP = binary2npy_express(in_path+in_file, header_lines=header_lines, debug=debug) # Read the file
            branches       = ["RawADC","TimeStamp","NBinsWvf", "Sampling"]                               # Branches to be saved
            content        = [ADC,TIMESTAMP, ADC.shape[0], info["SAMPLING"][0]]                          # Content to be saved
            files          = os.listdir(out_path+out_folder)                                             # List of files in the output folder
            # branches       = ["RawADC","TimeStamp","NBinsWvf", "Sampling", "Label", "RawPChannel"]                                 # Branches to be saved
            # content        = [ADC,TIMESTAMP, ADC.shape[0], info["SAMPLING"][0], info["CHAN_LABEL"][j], int(info["CHAN_POLAR"][j])] # Content to be saved
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


### DEPRECATED --- UPDATE ###
def root2npy(runs, channels, info={}, debug=False): ### ACTUALIZAR COMO LA DE BINARIO ###
    '''
    \nDumper from .root format to npy tuples. 
    \nInput are root input file path and npy outputfile as strings. 
    \nDepends on uproot, awkward and numpy. 
    \nSize increases x2 times. 
    \nNEEDS UPDATE!! (see binary2npy)
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
            my_dict["NBinsWvf"] = my_dict["RawADC"][0].shape[0]
            my_dict["Sampling"] = info["SAMPLING"][0]
            # my_dict["Label"]       = info["CHAN_LABEL"][j]
            # my_dict["RawPChannel"] = int(info["CHAN_POLAR"][j])

            np.save(out_path+out_file,my_dict)
            
            if debug:
                print_colored(my_dict.keys(), "DEBUG")
                print_colored("Saved data in:" +str(out_path+out_file), "DEBUG")
                print_colored("----------------------\n", "DEBUG")

        except FileNotFoundError: print("--- File %s was not foud!!! \n"%in_file)


#===========================================================================#
#***************************** KEYS ****************************************#
#===========================================================================#

def check_key(OPT, key):
    ''' 
    \nChecks if the given key is included in the dictionary OPT.
    \nReturns a bool. (True if it finds the key)
    '''

    try:   OPT[key]; return True   # If the key is found, return True 
    except KeyError: return False  # If the key is not found, return False

def print_keys(my_runs, debug=False):
    '''
    \nPrints the keys of the run_dict which can be accesed with run_dict[runs][channels][BRANCH] 
    '''
    try:
        for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
            print("------------------------------------------------------------------------------------------------------------------------------------------------------")
            print("Dictionary keys --> ",list(my_runs[run][ch].keys()))
            print("------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    except KeyError: print_colored("Empty dictionary. No keys to print.", "ERROR")
    if debug: print_colored("Keys printed", "DEBUG")

def delete_keys(my_runs, keys, debug=False):
    '''
    \nDelete the keys list introduced as 2nd variable
    '''

    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        try:   del my_runs[run][ch][key]      # Delete the key
        except KeyError: print_colored("*EXCEPTION: [Run%i - Ch%i - %s] key combination is not found in my_runs"%(run,ch,key), "WARNING")   
    if debug: print_colored("Keys deleted: %s"%keys, "DEBUG")

#===========================================================================#
#************************** LOAD/SAVE NPY **********************************#
#===========================================================================# 

def get_preset_list(my_run, path, folder, preset, option, debug = False):
    '''
    \nReturn as output presets lists for load/save npy files.
    \n**VARIABLES**:
    \n- my_run: my_runs[run][ch]
    \n- path: saving path
    \n- folder: saving in/out folder
    \n- preset: 
       (a) "ALL": all the existing keys/branches
       (b) "ANA": only Ana keys/branches (removing RAW info)
       (c) "INT": only Charge*, Ave* keys/branches
       (d) "RAW": only Raw information i.e loaded from Raw2Np + Raw* keys
       (e) "EVA": all the existing keys/branches EXCEPT ADC
       (f) "DEC": only DEC info i.e Wiener*, Gauss*, Dec* or Charge* keys
       (g) "CAL": only Charge* keys
       (h) "WVF": only Wvf* keys
    \n- option: 
       (a) "LOAD": takes the os.listdir(path+folder) as brach_list (IN)
       (b) "SAVE": takes the my_run.keys() as branch list (OUT)
    '''

    dict_option = dict()
    dict_option["LOAD"] = os.listdir(path+folder)
    dict_option["SAVE"] = my_run.keys()

    if preset == "ALL":  # Save all branches
        branch_list = dict_option[option]; aux = []
        for key in branch_list:
            if key and not "Label" in key and not "PChannel" in key and not "UnitsDict" in key and not "MyCuts" in key: aux.append(key)
        branch_list = aux

    elif preset == "ANA": # Remove Raw, Dict and Cuts branches
        branch_list = dict_option[option]; aux = ["RawADC"]
        for key in branch_list:
            if not "ADC" in key and not "Dict" in key and not "Cuts" in key and not "Gauss" in key and not "Label" in key and not "PChannel" in key: aux.append(key)
        branch_list = aux

    elif preset == "RAW":  # Save aux + Raw branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "Raw" in key and not "Label" in key and not "PChannel" in key: aux.append(key) 
        branch_list = aux

    elif preset == "EVA": # Remove ADC, Dict and Cuts branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if not "ADC" in key and not "Dict" in key and not "Cuts" in key and not "Label" in key and not "PChannel" in key: aux.append(key) # and key not in aux # add??
        branch_list = aux

    elif preset == "DEC": # Save aux + Gauss*, Wiener*, Dec* and Charge* branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "Gauss" in key or "Wiener" in key or "Dec" in key and not "Label" in key and not "PChannel" in key: aux.append(key) # and key not in aux # add??
        branch_list = aux

    elif preset == "CAL": # Save aux + Charge* branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "Charge" in key and key not in aux and not "Label" in key and not "PChannel" in key: aux.append(key)
        branch_list = aux

    elif preset == "WVF": # Save aux + Wvf* branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "Wvf" in key and key not in aux and not "Label" in key and not "PChannel" in key: aux.append(key)
        branch_list = aux

    elif preset == "INT": # Save aux + Wvf* branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "Wvf" in key or "Charge" in key and key not in aux and not "Label" in key and not "PChannel" in key: aux.append(key)
        branch_list = aux

    elif preset == "FFT": # Save aux + Wvf* branches
        branch_list = dict_option[option]; aux = ["TimeStamp"]
        for key in branch_list:
            if "MeanFFT" in key or "Freq" in key and key not in aux and not "Label" in key and not "PChannel" in key: aux.append(key)
        branch_list = aux
    
    else:
        print_colored("Preset not found. Returning all the branches.", "WARNING")
        raise ValueError("Preset not found. Returning all the branches.")

    if debug: print_colored("Branch list: "+str(branch_list), "DEBUG")
    return branch_list

def load_npy(runs, channels, info, preset="", branch_list = [], debug = False, compressed=True):
    '''
    \nStructure: run_dict[runs][channels][BRANCH] 
    \nLoads the selected channels and runs, for simplicity, all runs must have the same number of channels
    \nPresets can be used to only load a subset of desired branches. ALL is default.
    \n**VARIABLES**:
    \n- runs: list of runs to load
    \n- channels: list of channels to load
    \n- preset:
       (a) "ALL": all the existing keys/branches
       (b) "ANA": only Ana keys/branches (removing RAW info)
       (c) "INT": only Charge*, Ave* keys/branches
       (d) "RAW": only Raw information i.e loaded from Raw2Np + Raw* keys
       (e) "EVA": all the existing keys/branches EXCEPT ADC
       (f) "DEC": only DEC info i.e Wiener*, Gauss*, Dec* or Charge* keys
       (g) "CAL": only Charge* keys
    \n- branch_list: list of branches to load
    \n- info: dictionary with the info of the run
    \n- debug: if True, print debug info
    '''
    if debug: print_colored("\nLoading npy files...", "DEBUG")
    path = info["PATH"][0]+info["MONTH"][0]+"/npy/"

    my_runs = dict()
    my_runs["NRun"]     = runs
    my_runs["NChannel"] = channels
    aux_PChannel = dict(zip(info["CHAN_TOTAL"], info["CHAN_POLAR"]))
    aux_Label    = dict(zip(info["CHAN_TOTAL"], info["CHAN_LABEL"]))

    for run in runs:
        my_runs[run]=dict()
        for ch_idx,ch in enumerate(channels):
            my_runs[run][ch]=dict()
            in_folder="run"+str(run).zfill(2)+"_ch"+str(ch)+"/"
            if preset!="": branch_list = get_preset_list(my_runs[run][ch], path, in_folder, preset, "LOAD", debug) # Get the branch list if preset is used
            for branch in branch_list:   
                # try:
                if compressed:
                    my_runs[run][ch][branch.replace(".npz","")] = np.load(path+in_folder+branch.replace(".npz","")+".npz",allow_pickle=True, mmap_mode="w+")["arr_0"]     
                    if branch.__contains__("RawADC"):my_runs[run][ch][branch.replace(".npz","")]=my_runs[run][ch][branch.replace(".npz","")].astype(float)
                else:
                    my_runs[run][ch][branch.replace(".npy","")] = np.load(path+in_folder+branch.replace(".npy","")+".npy",allow_pickle=True, mmap_mode="w+").item()
                    if branch.__contains__("RawADC"):my_runs[run][ch][branch.replace(".npy","")]=my_runs[run][ch][branch.replace(".npy","")].astype(float)
                # except FileNotFoundError: print_colored("\nRun %i, channels %i --> NOT LOADED (FileNotFound)"%(run,ch), "ERROR")


            my_runs[run][ch]["Label"]    = aux_Label[ch]
            my_runs[run][ch]["PChannel"] = aux_PChannel[ch]
            my_runs[run][ch]["Sampling"] = float(info["SAMPLING"][0])
                 
            print_colored("\n....... Load npy runs %s & %s channels --> DONE! .......\n"%(runs,channels), color="SUCCESS", bold=True)
            del branch_list # Delete the branch list to avoid loading the same branches again
    return my_runs

def save_proccesed_variables(my_runs, info, preset = "", branch_list = [], force=False, compressed=True, debug = False):
    '''
    \nSaves the processed variables an npx file.
    \n**VARIABLES**:
    \n- my_runs: dictionary with the runs and channels to be saved
    \n- preset: preset to be used to save the variables
    \n- branch_list: list of branches to be saved
    \n- info: dictionary with the path and month to be used
    \n- force: if True, the files will be overwritten
    \n- debug: if True, the function will print the branches that are being saved
    \n- compressed: if True, the files will be saved as npz, if False, as npy
    '''

    aux = copy.deepcopy(my_runs) # Save a copy of my_runs with all modifications and remove the unwanted branches in the copy
    path = info["PATH"][0]+info["MONTH"][0]+"/npy/"
    for run in aux["NRun"]:
        for ch in aux["NChannel"]:
            print_colored("\n--> Saving Computed Variables (according to preset %s)!"%(preset), color="INFO", bold=True)
            out_folder = "run"+str(run).zfill(2)+"_ch"+str(ch)+"/"
            os.makedirs(name=path+out_folder,exist_ok=True)
            files = os.listdir(path+out_folder)
            if not branch_list: branch_list = get_preset_list(my_runs[run][ch],path, out_folder, preset, "SAVE", debug)
            for key in branch_list:
                key = key.replace(".npz","")

                # If the file already exists, skip it
                if key+".npz" in files and force == False: 
                    if debug: print_colored("\tFile (%s.npz) alredy exists"%key, "DEBUG")
                    continue 
                
                # If the file already exists and force is True, overwrite it
                elif (key+".npz" in files or key+".npy" in files) and force == True:        
                    if compressed:
                        os.remove(path+out_folder+key+".npz")
                        np.savez_compressed(path+out_folder+key+".npz",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        print_colored("\tFile (%s.npz) OVERWRITTEN "%key, "WARNING")
                    else:
                        os.remove(path+out_folder+key+".npy")
                        np.save(path+out_folder+key+".npy",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        print_colored("\tFile (%s.npy) OVERWRITTEN "%key, "WARNING")
                
                # If the file does not exist, create it
                elif check_key(aux[run][ch], key): 
                    np.savez_compressed(path+out_folder+key+".npz",aux[run][ch][key])
                    os.chmod(path+out_folder+key+".npz", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    print_colored("\tSaving NEW file: %s.npz"%key, "SUCCESS")
                    if debug: print_colored("\t"+path+out_folder+key+".npz", "DEBUG")
                    if not compressed:
                        np.save(path+out_folder+key+".npy",aux[run][ch][key])
                        os.chmod(path+out_folder+key+".npy", stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        print_colored("\tSaving NEW file: %s.npy"%key, "SUCCESS")
                        if debug: print_colored("\t"+path+out_folder+key+".npy","DEBUG")

    print_colored("--> Saved Data Succesfully!!!", "SUCCESS")
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

def npy2root(my_runs, debug = False):
    '''
    \nConverts the npy files to root TTree files by converting the dictionaries to a RDataFrame from ROOT & using the snapshot method.
    \n**VARIABLES:**
    \n- my_runs: dictionary with the runs and channels to be saved
    \n- debug: if True, the function will print the branches that are being saved
    '''

    # Create the ROOT dataframe
    df = ROOT.RDF.FromNumpy(my_runs)
    return df

    # Create the ROOT file
    f = ROOT.TFile.Open("test.root","RECREATE")
    # Create the ROOT tree
    tree = df.Snapshot("tree", "test.root")
    # Save the ROOT file
    f.Write()
    f.Close()

    f2 = ROOT.TFile("test.root")
    t = f2.myTree
    print("These are all the columns available to this dataframe:")
    for branch in t.GetListOfBranches():
        print("Branch: %s" %branch.GetName())

    if debug: print_colored("npy2root --> DONE!\n", "SUCCESS")

def npy2df(my_runs, debug = False):
    '''
    \nConverts the npy files to a pandas dataframe.
    \n**VARIABLES:**
    \n- my_runs: dictionary with the runs and channels to be saved
    \n- debug: if True, the function will print the branches that are being saved
    '''
    # From my_runs.keys() remove all keys that are not a dictionary
    keys = list(my_runs.keys())
    for key in keys:
        if not isinstance(my_runs[key], dict):
            my_runs.pop(key)
            
    df = pd.DataFrame.from_dict({
        (i,j): my_runs[i][j] 
        for i in my_runs.keys() 
        for j in my_runs[i].keys()},
        orient='index')
    
    if debug: print_colored("npy2df --> DONE!\n", "SUCCESS")
    return df