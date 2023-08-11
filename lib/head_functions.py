import sys
from lib.io_functions import check_key, print_colored, read_input_file

def get_flag_dict():
    '''
    This function returns a dictionary with the available flags for the macros.
    
    **RETURNS:**

        - **flag_dict** (*dict*) - Dictionary with the available flags for the macros.
    '''
    flag_dict = {("-i","--input_file"):"input_file",
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
                        print("Please provide agument for flag %s"%flag_dict[flag])
                        exit()

    user_input = select_input_file(user_input, debug=debug)
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
    new_user_input = user_input.copy()
    for key_label in new_input_list:
        if check_key(user_input, key_label) == False:
            new_user_input[key_label]= input("Please select %s (separated with commas): "%key_label).split(",")
        else:
            if debug: print("Using %s from user input"%key_label)
    
    return new_user_input

def select_input_file(user_input, debug=False):
    '''
    This function asks the user to select the input file.

    **VARIABLES:**

        - **user_input** (*dict*) - Dictionary with the user input.
    '''
    import inquirer
    import os
    
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

    import numpy as np
    
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