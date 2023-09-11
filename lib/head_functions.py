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
        ("-k","--key"):"key \t(AnaADC, RawADC, etc.)",
        ("-v","--variables"): "variables \t(ChargeAveRange, ChargeRange0, etc.)",
        ("-r","--runs"):"runs \t(optional)",
        ("-c","--channels"):"channels \t(optional)",
        ("-f","--filter"): "filter \t(optional)",
        ("-d","--debug"):"debug \t(True/False)"}
    
    return flag_dict

def initialize_macro(macro, input_list=["input_file","debug"], default_dict={}, debug=False):
    '''
    This function initializes the macro by reading the input file and the user input.
    
    **VARIABLES:**

        - **macro** (*str*) - Name of the macro to be executed.
    '''
    from .io_functions import print_colored,check_key

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
                        if flag[1].split("--")[1] != "filter":
                            user_input[flag[1].split("--")[1]] = sys.argv[sys.argv.index(arg)+1].split(",")
                            print_colored("Using %s from command line"%flag_dict[flag],"INFO")
                        else:
                            if sys.argv[sys.argv.index(arg)+1].split(",")[0].lower() in ['true', '1', 't', 'y', 'yes']:  
                                user_input = select_input_file(user_input, debug=debug)
                                user_input["input_file"] = user_input["input_file"][0]
                                user_input["cuts"] = apply_cuts(user_input, debug=debug)
                            if sys.argv[sys.argv.index(arg)+1].split(",")[0].lower() in ['false', '0', 'f', 'n', 'no']: 
                                user_input["cuts"] = {'cut_df': [False], 'cut_lin_rel': [False], 'cut_peak_finder': [False]}

                    except IndexError:
                        print("Please provide argument for flag %s"%flag_dict[flag])
                        exit()
    if check_key(user_input, "input_file") == False:
        user_input = select_input_file(user_input, debug=debug)
        user_input["input_file"] = user_input["input_file"][0]
    user_input = update_user_input(user_input,input_list,debug=debug)
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
    defaults = {"load_preset":"ANA","save_preset":"ANA","key":"AnaADC","variables":"AnaPeakAmp","runs":"1","channels":"0","debug":"y"}
    flags = {"load_preset":"-l","save_preset":"-s","key":"-k","variables":"-v","runs":"-r","channels":"-c","debug":"-d"}
    for key_label in new_input_list:
        if check_key(user_input, key_label) == False:
            if key_label != "cuts":
                q = [ inquirer.Text(key_label, message="Please select %s [flag: %s]"%(key_label,flags[key_label]), default=defaults[key_label]) ]
                new_user_input[key_label] =  inquirer.prompt(q)[key_label].split(",")
            else:  new_user_input["cuts"] = apply_cuts(user_input, debug=debug)
                
        else: pass
            # if debug: print("Using %s from user input"%key_label)
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
        q = [ inquirer.List("input_file", message="Please select input file [flag: -i]", choices=file_names, default="TUTORIAL") ]
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
    for default_key in default_dict:
        if check_key(new_user_input, default_key) == False:
            runs = []
            for key in default_dict[default_key]:
                if check_key(info, key):
                    for run in info[key]:
                        if run not in runs:
                            runs.append(run)
            new_user_input[default_key] = runs
            if new_user_input["debug"]:print_colored("No runs provided. Using all %s from input file. %s"%(default_key,runs),"WARNING")

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
    from .io_functions import check_key, print_colored,read_input_file,cuts_info2dict

    
    cuts_choices = ["cut_df","cut_lin_rel","cut_peak_finder"]
    info = read_input_file(user_input["input_file"])
    cut_dict = cuts_info2dict(info)
    for cut in cuts_choices:
        if cut_dict[cut][0] == True: 
            if debug: print_colored("Using cuts options %s"%cut_dict,"INFO")
            return cut_dict
        else:
            if check_key(user_input, "cuts") == False:

                q = [ inquirer.Checkbox("cuts", message="Please select the cuts you want to apply", choices=cuts_choices) ]
                my_cuts = [inquirer.prompt(q)["cuts"]][0]
                cut_dict = dict.fromkeys(cuts_choices)
                for cut in cuts_choices:
                    if cut in my_cuts:
                        if cut == "cut_df":
                            channels = [ inquirer.Text("channels", message="Please select channels for applying **%s**"%cut, default="0,1") ]
                            key = [ inquirer.Text("key", message="Please select key for applying **%s**"%cut, default="AnaPedSTD") ]
                            logic = [ inquirer.Text("logic", message="Please select logic for applying **%s**"%cut, default="bigger_than") ]
                            value = [ inquirer.Text("value", message="Please select value for applying **%s**"%cut, default="1") ]
                            inclusive = [ inquirer.Text("inclusive", message="Please select inclusive for applying **%s**"%cut, default="False") ]
                            cut_dict[cut] = [True, inquirer.prompt(channels)["channels"].split(','),inquirer.prompt(key)["key"].split(','), inquirer.prompt(logic)["logic"].split(','), inquirer.prompt(value)["value"].split(','), inquirer.prompt(inclusive)["inclusive"].split(',')]
                        if cut == "cut_lin_rel":
                            key = [ inquirer.Text("key", message="Please select 2 keys for applying **%s**"%cut, default="AnaPeakAmp,AnaChargeAveRange") ]
                            compare = [ inquirer.Text("compare", message="NONE, RUNS, CHANNELS to decide the histogram to use", default="NONE") ]
                            cut_dict[cut] = [True, inquirer.prompt(key)["key"].split(','), inquirer.prompt(compare)["compare"]]
                        if cut == "cut_peak_finder":
                            n_peaks = [ inquirer.Text("n_peaks", message="Please select number of peaks for applying **%s**"%cut, default="1") ]
                            cut_dict[cut] = [True, inquirer.prompt(n_peaks)["n_peaks"]]

                    else: cut_dict[cut] = [False]

            if debug: print_colored("Using cuts options %s"%cut_dict,"INFO")
            return cut_dict

# Function to read and print the content of a text file
def read_and_print_text_file(filename):
    from .io_functions import print_colored

    try:
        first_words = []
        with open(filename, 'r') as file:
            content = file.read()
            for l,line in enumerate(content.strip().split()):
                if ":" in line: first_words.append(line)
            print_colored("\nCurrent visualization parameters:","INFO")
            print(content)
            print("\n")
        return content, first_words
    except FileNotFoundError: print_colored(f"The file '{filename}' does not exist.","ERROR"); return None

# Function to update a specific line in the text content
def update_line(filename, content, first_words, line_label, new_text):
    read_lines  = content.split('\n')
    line_number = np.where(np.asarray(first_words) == line_label)[0][0]
    new_lines   = read_lines
    new_lines[line_number] = line_label + " " + new_text
    save_lines = [i + j for i,j in  zip(new_lines,["\n"]*int(len(new_lines)-1)+[""])]

    with open(filename, 'w') as file:
        for line in save_lines: file.write(line)

    print("UPDATED",save_lines)
    print(f"Content has been updated and saved to '{filename}'.")

    return save_lines

def opt_selector(filename = "VisConfig.txt", debug=False):
    from .io_functions import print_colored
    content, first_words = read_and_print_text_file(filename)
    if content:
        q = [ inquirer.List("change", message="Do you want to change a line? (yes/no)", choices=["yes","no"], default="no") ]
        change_line =  inquirer.prompt(q)["change"].strip().lower()
        if change_line in ["yes","y","true","1"]:
            q = [ inquirer.Checkbox("lines", message="Choose the lines to change", choices=first_words) ]
            line_label =  inquirer.prompt(q)["lines"]
            for line in line_label:
                new_text = input(f"Enter the new text for line {line} ")
                updated_content = update_line(filename, content, first_words, line, new_text)
            my_opt = {j.split(':')[0]:j.split(':')[1].strip() for j in updated_content}
    
        else: my_opt = {j.split(':')[0]:j.split(':')[1].strip() for j in content.split('\n')}
        
        return my_opt