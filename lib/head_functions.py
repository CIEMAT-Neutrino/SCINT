import sys, inquirer, os
import numpy as np
import icecream as ic
from .io_functions import print_colored, check_key, read_input_file, cuts_info2dict

def get_flag_dict():
    '''
    \nThis function returns a dictionary with the available flags for the macros.
    \n**RETURNS:**
    \n- **flag_dict** (*dict*) - Dictionary with the available flags for the macros.
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

def initialize_macro(macro, input_list = ["input_file","debug"], default_dict = {}, debug = False):
    '''
    \nThis function initializes the macro by reading the input file and the user input.
    \n**VARIABLES:**
    \n- **macro** (*str*) - Name of the macro to be executed.
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
                        print_colored("Using %s from command line %s"%(flag_dict[flag],sys.argv[sys.argv.index(arg)+1].split(",")),"INFO")
                    except IndexError:
                        print("Provide argument for flag %s"%flag_dict[flag])
                        exit()
    if check_key(user_input, "input_file") == False:
        user_input = select_input_file(user_input, debug = debug)
        user_input["input_file"] = user_input["input_file"]
    
    info = read_input_file(user_input["input_file"][0], debug = debug)
    user_input, info = update_user_input(user_input, input_list, info, debug = debug)
    user_input["debug"] = user_input["debug"][0].lower() in ['true', '1', 't', 'y', 'yes']
    user_input = use_default_input(user_input, default_dict, info, debug = debug)

    if debug:
        print_colored("\nUser input:","INFO")
        ic.ic(user_input)
    return user_input, info

def update_user_input(user_input, new_input_list, info, debug=False):
    '''
    \nThis function updates the user input by asking the user to provide the missing information.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    \n- **new_input_list** (*list*) - List with the keys of the user input that need to be updated.
    '''

    new_user_input = user_input.copy()
    defaults = {"load_preset":"ANA","save_preset":"ANA","key":"AnaADC","variables":"AnaPeakAmp","runs":"1","channels":"0","debug":"y"}
    flags = {"load_preset":"-l","save_preset":"-s","key":"-k","variables":"-v","runs":"-r","channels":"-c","debug":"-d"}
    for key_label in new_input_list:
        if check_key(user_input, key_label) == False:
            if key_label != "filter":
                q = [ inquirer.Text(key_label, message=" select %s [flag: %s]"%(key_label,flags[key_label]), default=defaults[key_label]) ]
                new_user_input[key_label] =  inquirer.prompt(q)[key_label].split(",")
                # print_colored("Using %s from user input %s"%(key_label,new_user_input[key_label]),"WARNING")
            else:
                new_user_input["filter"] = apply_cuts(user_input, info, debug=debug)
                print_colored("Using %s from user input %s"%(key_label,new_user_input[key_label]),"WARNING")
        else:
            # print_colored("Using %s from user input %s"%(key_label,new_user_input[key_label]),"WARNING")
            pass
            # if debug: print("Using %s from user input"%key_label)
    return new_user_input, info

def select_input_file(user_input, debug=False):
    '''
    \nThis function asks the user to select the input file.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    '''
    
    new_user_input = user_input.copy()
    if check_key(user_input, "input_file") == False:
        file_names = [file_name.replace(".txt", "") for file_name in os.listdir('../input')]
        q = [ inquirer.List("input_file", message=" select input file [flag: -i]", choices=file_names, default="TUTORIAL") ]
        new_user_input["input_file"] = [inquirer.prompt(q)["input_file"]]
    if debug: print_colored("Using input file %s"%new_user_input["input_file"][0],"INFO")
    return new_user_input

def use_default_input(user_input, default_dict, info, debug = False):
    '''
    \nThis function updates the user input by asking the user to provide the missing information.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    \n- **info** (*dict*) - Dictionary with the information from the input file.
    '''
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
            if new_user_input["debug"]: print_colored("No %s provided. Using all %s from input file. %s"%(default_key,default_key,runs),"WARNING")
    return new_user_input

def print_macro_info(macro, debug=False):
    f = open('info/'+macro+'.txt', 'r')
    file_contents = f.read()
    print (file_contents+"\n")
    f.close
    if debug: print_colored("....... Debug Mode Activated! .......", "DEBUG")

def print_header():
    f = open('info/header.txt', 'r')
    file_contents = f.read()
    print (file_contents)
    f.close
    print_colored("....... Starting Macro .......", "INFO")

def apply_cuts(user_input, info, debug=False):
    '''
    \nThis function asks the user to select the cuts to be apply to your events.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    '''
    cuts_choices = ["cut_df","cut_lin_rel","cut_peak_finder"]
    cut_dict = cuts_info2dict(user_input, info, debug=True)
    for cut in cuts_choices:
        if cut_dict[cut][0] == True: 
            # if debug: print_colored("Using cuts options %s"%cut_dict,"INFO")
            return cut_dict
        if cut_dict[cut][0] == False:
            ask4cuts = True
            q = [ inquirer.Checkbox("filter", message=" select the cuts you want to apply", choices=cuts_choices) ]
            my_cuts = [inquirer.prompt(q)["filter"]][0]
            for cut in cuts_choices:
                if cut in my_cuts:
                    if cut == "cut_df":
                        while ask4cuts:
                            if cut_dict[cut][0] != True: cut_dict[cut] = [True, []]
                            channels  = [ inquirer.Text("channels",  message="Select channels for applying **%s**"%cut, default="0,1") ]
                            key       = [ inquirer.Text("key",       message="Select key for applying **%s**"%cut, default="AnaPedSTD") ]
                            logic     = [ inquirer.Text("logic",     message="Select logic for applying **%s**"%cut, default="bigger") ]
                            value     = [ inquirer.Text("value",     message="Select value for applying **%s**"%cut, default="1") ]
                            inclusive = [ inquirer.Text("inclusive", message="Select inclusive for applying **%s**"%cut, default="False") ]
                            cut_dict[cut][1].append([inquirer.prompt(channels)["channels"].split(','),inquirer.prompt(key)["key"], inquirer.prompt(logic)["logic"], float(inquirer.prompt(value)["value"]), inquirer.prompt(inclusive)["inclusive"].lower() in ['true', '1', 't', 'y', 'yes']])
                            ask4cuts = input("\nDo you want to add another cut? (y/n) ").lower() in ['true', '1', 't', 'y', 'yes']

                    if cut == "cut_lin_rel":
                        while ask4cuts:
                            if cut_dict[cut][0] != True: cut_dict[cut] = [True, []]
                            key = [ inquirer.Text("key", message="Select 2 keys for applying **%s**"%cut, default="AnaPeakAmp,AnaChargeAveRange") ]
                            compare = [ inquirer.Text("compare", message="NONE, RUNS, CHANNELS to decide the histogram to use", default="NONE") ]
                            cut_dict[cut][1].append([inquirer.prompt(key)["key"].split(','), inquirer.prompt(compare)["compare"]])
                            ask4cuts = input("\nDo you want to add another cut? (y/n) ").lower() in ['true', '1', 't', 'y', 'yes']

                    if cut == "cut_peak_finder":
                        while ask4cuts:
                            if cut_dict[cut][0] != True: cut_dict[cut] = [True, []]
                            n_peaks = [ inquirer.Text("n_peaks", message="Select number of peaks for applying **%s**"%cut, default="1") ]
                            cut_dict[cut][1].append([inquirer.prompt(n_peaks)["n_peaks"]])
                            ask4cuts = input("\nDo you want to add another cut? (y/n) ").lower() in ['true', '1', 't', 'y', 'yes']

            if debug: print_colored("Using cuts options %s"%cut_dict,"INFO")
            return cut_dict

# Function to read and print the content of a text file
def read_and_print_text_file(filename):
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
def update_line(filename, content, first_words, line_label, new_text, debug = False):
    read_lines  = content.split('\n')
    line_number = np.where(np.asarray(first_words) == line_label)[0][0]
    new_lines   = read_lines
    new_lines[line_number] = line_label + " " + new_text
    save_lines = [i + j for i,j in  zip(new_lines,["\n"]*int(len(new_lines)-1)+[""])]

    with open(filename, 'w') as file:
        for line in save_lines: file.write(line)
    file.close()
    # print("UPDATED",save_lines)
    if debug: print_colored("Content has been updated and saved to '%s'."%filename, "DEBUG")

    return save_lines

def opt_selector(filename = "VisConfig.txt", debug = False):
    content, first_words = read_and_print_text_file(filename)
    # if content:
    q = [ inquirer.List("change", message="Do you want to change a line? (yes/no)", choices=["yes","no"], default="no") ]
    change_line =  inquirer.prompt(q)["change"].strip().lower()
    if change_line in ["yes","y","true","1"]:
        q = [ inquirer.Checkbox("lines", message="Choose the lines to change", choices=first_words) ]
        line_label =  inquirer.prompt(q)["lines"]
        for line in line_label:
            new_text = input(f"Enter the new text for line {line} ")
            updated_content = update_line(filename, content, first_words, line, new_text, debug = debug)
        my_opt = {j.split(':')[0]:j.split(':')[1].strip() for j in updated_content}

    else: my_opt = {j.split(':')[0]:j.split(':')[1].strip() for j in content.split('\n')}
    
    my_opt = read_input_file(filename.split(".txt")[0],path="",
        BOOLEAN=["ALIGN","MICRO_SEC","NORM","LOGX","LOGY","LOGZ","SHOW_PARAM","CHARGEDICT","PEAK_FINDER","SAME_PLOT","LEGEND","SHOW","TERMINAL_MODE","PRINT_KEYS","SCINT_FIT","STATS"],
        STRINGS=["SHOW_AVE","CHARGE_KEY","COMPARE","FIT","STYLE"],
        NUMBERS=["CUTTED_WVF","ACCURACY"],
        DOUBLES=["THRESHOLD","WIDTH","PROMINENCE"],debug=False)
    # Reformat the dict to select the first element of the list of each entry
    for key in my_opt:
        try: my_opt[key] = my_opt[key][0]
        except IndexError: pass

    if debug:
        print_colored("\nUsing visualization options:","INFO")
        ic.ic(my_opt)
    return my_opt