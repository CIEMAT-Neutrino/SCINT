import sys, inquirer, os
import numpy as np

def get_flag_dict():
    '''
    This function returns a dictionary with the available flags for the macros.
    
    **RETURNS:**

        - **flag_dict** (*dict*) - Dictionary with the available flags for the macros.
    '''
    flag_dict = {("-i","--input_file"):"input_file",
        ("-l","--load_preset"):"load_preset \t(RAW, ANA, etc.)",
        ("-s","--save_preset"): "save_preset \t(RAW, ANA, etc.)",
        ("-k","--key"):"key \t(ADC, RawADC, etc.)",
        ("-v","--variables"): "variables \t(ChargeAveRange, ChargeRange0, etc.)",
        ("-r","--runs"):"runs \t(optional)",
        ("-c","--channels"):"channels \t(optional)",
        ("-d","--debug"):"debug \t(True/False)"}
    
    return flag_dict

def initialize_macro(macro, input_list=["input_file","debug"], default_dict={}, debug=False):
    '''
    This function initializes the macro by reading the input file and the user input.
    
    **VARIABLES:**

        - **macro** (*str*) - Name of the macro to be executed.
    '''
    from .io_functions import print_colored

    flag_dict = get_flag_dict()
    user_input = dict()
    
    print_header()
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-h" or arg == "--help":
                for flag in flag_dict:
                    print_macro_info(macro)
                    print_colored("Usage: python3 %s.py -i config_file *--flags"%macro,color="white",bold=True)
                    print_colored("Available Flags:","INFO",bold=True)
                    for flag in flag_dict:
                        print_colored("%s: %s"%(flag[0],flag_dict[flag]),"INFO")
                    exit()

            for flag in flag_dict:
                if arg == flag[0] or arg == flag[1]:
                    try:
                        user_input[flag[1].split("--")[1]] = sys.argv[sys.argv.index(arg)+1].split(",")
                        print_colored("Using %s from command line"%flag_dict[flag],"INFO")
                    except IndexError:
                        print("Please provide argument for flag %s"%flag_dict[flag])
                        exit()

    user_input = select_input_file(user_input, debug=debug)
    if "cuts" in input_list: user_input = apply_cuts(user_input, debug=debug)
    user_input = update_user_input(user_input,input_list,debug=debug)
    
    user_input["input_file"] = user_input["input_file"][0]
    user_input["debug"] = user_input["debug"][0].lower() in ['true', '1', 't', 'y', 'yes']
    user_input = use_default_input(user_input, default_dict, debug=debug)

    if debug: print_colored("User input: %s"%user_input,"INFO")
    return user_input

def update_user_input(user_input,new_input_list,debug=False):
    '''
    This function updates the user input by asking the user to provide the missing information.
    
    **VARIABLES:**

        - **user_input** (*dict*) - Dictionary with the user input.
        - **new_input_list** (*list*) - List with the keys of the user input that need to be updated.
    '''
    from .io_functions import check_key

    new_user_input = user_input.copy()
    for key_label in new_input_list:
        if check_key(user_input, key_label) == False:
            new_user_input[key_label]= input("Please select %s (separated with commas): "%key_label).split(",")
        else:
            # if debug: print("Using %s from user input"%key_label)
            pass
    
    return new_user_input

def select_input_file(user_input, debug=False):
    '''
    This function asks the user to select the input file.

    **VARIABLES:**

        - **user_input** (*dict*) - Dictionary with the user input.
    '''
    from .io_functions import check_key, print_colored
    
    new_user_input = user_input.copy()
    if check_key(user_input, "input_file") == False:
        file_names = [file_name.replace(".txt", "") for file_name in os.listdir('../input')]
        q = [ inquirer.List("input_file", message="Please select input file", choices=file_names, default="TUTORIAL") ]
        new_user_input["input_file"] = [inquirer.prompt(q)["input_file"]]
    if debug: print_colored("Using input file %s"%new_user_input["input_file"][0],"INFO")
    return new_user_input

def use_default_input(user_input, default_dict, debug=False):
    '''
    This function updates the user input by asking the user to provide the missing information.

    **VARIABLES:**

        - **user_input** (*dict*) - Dictionary with the user input.
        - **info** (*dict*) - Dictionary with the information from the input file.
    '''
    from .io_functions import check_key, print_colored, read_input_file
    
    info = read_input_file(user_input["input_file"])

    new_user_input = user_input.copy()
    if check_key(new_user_input, "runs") == False:
        runs = []
        for key in default_dict["runs"]:
            if check_key(info, key):
                for run in info[key]:
                    if run not in runs:
                        runs.append(run)
        new_user_input["runs"] = runs
        if new_user_input["debug"]:print_colored("No runs provided. Using all runs from input file. %s"%runs,"WARNING")

    if check_key(user_input, "channels") == False:
        channels = []
        for key in default_dict["channels"]:
            if check_key(info, key):
                for channel in info[key]:
                    if channel not in channels:
                        channels.append(channel)
        new_user_input["channels"] = channels
        if new_user_input["debug"]: print_colored("No channels provided. Using all channels from input file. %s"%channels,"WARNING")
    return new_user_input

def print_macro_info(macro, debug=False):
    f = open('../info/'+macro+'.txt', 'r')
    file_contents = f.read()
    print (file_contents+"\n")
    f.close
    if debug: print("----- Debug mode activated -----")

def print_header():
    f = open('../info/header.txt', 'r')
    file_contents = f.read()
    print (file_contents)
    f.close
    print("----- Starting macro -----")

def apply_cuts(user_input, debug=False):
    '''
    This function asks the user to select the cuts to be apply to your events.

    **VARIABLES:**

        - **user_input** (*dict*) - Dictionary with the user input.
    '''
    from .io_functions import check_key, print_colored
    
    new_user_input = user_input.copy()
    if check_key(user_input, "cuts") == False:
        cuts_choices = ["cut_min_max","cut_ped_std","cut_lin_rel","cut_peak_finder","cut_min_max_sim"]
        q = [ inquirer.Checkbox("cuts", message="Please select input file", choices=cuts_choices) ]
        my_cuts = [inquirer.prompt(q)["cuts"]][0]
        cut_dict = dict.fromkeys(cuts_choices)
        for cut in cuts_choices:
            if cut in my_cuts:
                if cut == "cut_min_max":
                    key = [ inquirer.Text("key", message="Please select key for applying **%s**"%cut, default="PedSTD") ]
                    lim = [ inquirer.Text("lim", message="Please select limits for applying **%s**"%cut, default="-1,7.5") ]
                    chann2cut = [ inquirer.Text("ch2cut", message="Please select the CHANNELS to be cut", default="0,1") ]
                    apply_all = [ inquirer.Text("apply",  message="Do you what the cuts to be applied to all the LOADED channels?", default="y") ]
                    cut_dict[cut] = [True, inquirer.prompt(key)["key"], list(map(float, inquirer.prompt(lim)["lim"].split(','))), list(map(int, inquirer.prompt(chann2cut)["ch2cut"].split(','))), inquirer.prompt(apply_all)["apply"].lower() in ['true', '1', 't', 'y', 'yes']]
                if cut == "cut_ped_std":
                    n_std = [ inquirer.Text("n_std", message="Please select number of std for applying **%s**"%cut, default="2") ]
                    chann2cut = [ inquirer.Text("ch2cut", message="Please select the CHANNELS to be cut", default="0,1") ]
                    apply_all = [ inquirer.Text("apply",  message="Do you what the cuts to be applied to all the LOADED channels?", default="y") ]
                    cut_dict[cut] = [True, int(inquirer.prompt(n_std)["n_std"]),list(map(int, inquirer.prompt(chann2cut)["ch2cut"].split(','))), inquirer.prompt(apply_all)["apply"].lower() in ['true', '1', 't', 'y', 'yes']]
                if cut == "cut_lin_rel":
                    key = [ inquirer.Text("key", message="Please select 2 keys for applying **%s**"%cut, default="PeakAmp,ChargeAveRange") ]
                    compare = [ inquirer.Text("compare", message="NONE, RUNS, CHANNELS to decide the histogram to use", default="NONE") ]
                    cut_dict[cut] = [True, inquirer.prompt(key)["key"].split(','), inquirer.prompt(compare)["compare"]]
                if cut == "cut_peak_finder":
                    n_peaks = [ inquirer.Text("n_peaks", message="Please select number of peaks for applying **%s**"%cut, default="1") ]
                    cut_dict[cut] = [True, inquirer.prompt(n_peaks)["n_peaks"]]
                if cut == "cut_min_max_sim":
                    key = [ inquirer.Text("key", message="Please select key for applying **%s**"%cut, default="PeakAmp") ]
                    lim = [ inquirer.Text("lim", message="Please select limits for applying **%s**"%cut, default="20,50") ]
                    cut_dict[cut] = [True, inquirer.prompt(key)["key"].split(','), inquirer.prompt(lim)["lim"]]

            else: cut_dict[cut] = [False]

        new_user_input["cuts"] = cut_dict
        print(new_user_input)
    if debug: print_colored("Using cuts options %s"%new_user_input["cuts"],"INFO")
    return new_user_input