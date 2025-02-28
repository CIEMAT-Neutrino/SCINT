import sys, inquirer, os, yaml, ast
import numpy as np
from typing import Optional
from rich import print as print

from src.utils import get_project_root
from .io_functions import (
    print_colored,
    check_key,
    read_input_file,
    read_yaml_file,
    cuts_info2dict,
)

root = get_project_root()


def get_flag_dict():
    """
    This function returns a dictionary with the available flags for the macro.

    Args:
        None

    Returns:
        flag_dict (dict): Dictionary with the available flags for the macro.
    """
    flag_dict = {
        ("-c", "--channels"): "channels \t(optional)",
        ("-d", "--debug"): "debug \t(True/False)",
        ("-f", "--filter"): "filter \t(optional)",
        ("-g", "--group"): "group \t(True/False)",
        ("-i", "--input_file"): "input_file",
        ("-k", "--key"): "key \t(AnaADC, RawADC, etc.)",
        ("-pl", "--preset_load"): "preset_load \t(RAW, ANA, etc.)",
        ("-ps", "--preset_save"): "preset_save \t(RAW, ANA, etc.)",
        ("-v", "--variables"): "variables \t(ChargeAveRange, ChargeRange0, etc.)",
        ("-r", "--runs"): "runs \t(optional)",
        ("-s", "--save"): "save \t(optional)",
    }
    return flag_dict


def initialize_macro(
    macro, input_list=["input_file", "debug"], default_dict:Optional[dict]=None, debug=False
):
    """
    \nThis function initializes the macro by reading the input file and the user input.
    \n**VARIABLES:**
    \n- **macro** (*str*) - Name of the macro to be executed.
    """

    flag_dict = get_flag_dict()
    user_input = dict()

    if default_dict is None:
        default_dict = dict()
    else:
        if check_key(default_dict, "input_file") == True:
            user_input["input_file"] = default_dict["input_file"]

    print_header()
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "-h" or arg == "--help":
                for flag in flag_dict:
                    print_macro_info(macro)
                    print_colored(
                        "Usage: python3 %s.py -i config_file *--flags" % macro,
                        color="white",
                        styles=["bold"],
                    )
                    print_colored("Available Flags:", "INFO", styles=["bold"])
                    for flag in flag_dict:
                        print_colored("%s: %s" % (flag[0], flag_dict[flag]), "INFO")
                    exit()

            for flag in flag_dict:
                if arg == flag[0] or arg == flag[1]:
                    try:
                        user_input[flag[1].split("--")[1]] = sys.argv[
                            sys.argv.index(arg) + 1
                        ].split(",")
                        print_colored(
                            "Using %s from command line %s"
                            % (
                                flag_dict[flag],
                                sys.argv[sys.argv.index(arg) + 1].split(","),
                            ),
                            "INFO",
                        )
                    except IndexError:
                        print("Provide argument for flag %s" % flag_dict[flag])
                        exit()
    
    if check_key(user_input, "input_file") == False:
        user_input = select_input_file(user_input, debug=debug)
        user_input["input_file"] = user_input["input_file"]

    info = read_input_file(user_input["input_file"][0], debug=debug)
    user_input, info = update_user_input(user_input, input_list, info, debug=debug)
    for flag in ["group", "save", "debug"]:
        try:
            user_input[flag] = user_input[flag][0].lower() in [
                "true",
                "1",
                "t",
                "y",
                "yes",
            ]
        except KeyError:
            print("WARNING: No %s flag provided --> Using False as default." % flag)
    user_input = use_default_input(user_input, default_dict, info, debug=debug)

    if debug:
        print_colored("\nUser input:", "INFO")
        print(user_input)
    return user_input, info


def update_user_input(user_input, new_input_list, info, debug=False):
    """
    \nThis function updates the user input by asking the user to provide the missing information.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    \n- **new_input_list** (*list*) - List with the keys of the user input that need to be updated.
    """
    new_user_input = user_input.copy()
    defaults = {
        "preset_load": "ANA",
        "preset_save": "ANA",
        "key": "AnaADC",
        "variables": "AnaChargeAveRange",
        "runs": "1",
        "channels": "0",
        "group": "n",
        "save": "y",
        "debug": "y",
    }
    flags = {
        "preset_load": "-pl",
        "preset_save": "-ps",
        "key": "-k",
        "variables": "-v",
        "runs": "-r",
        "channels": "-c",
        "group": "-g",
        "save": "-s",
        "debug": "-d",
    }
    for key_label in new_input_list:
        if check_key(user_input, key_label) == False:
            if key_label != "filter":
                q = [
                    inquirer.Text(
                        key_label,
                        message=" select %s [flag: %s]" % (key_label, flags[key_label]),
                        default=defaults[key_label],
                    )
                ]
                new_user_input[key_label] = inquirer.prompt(q)[key_label].split(",")
                # print_colored("Using %s from user input %s"%(key_label,new_user_input[key_label]),"WARNING")
            else:
                new_user_input["filter"] = apply_cuts(user_input, info, debug=debug)
                print_colored(
                    "Using %s from user input %s"
                    % (key_label, new_user_input[key_label]),
                    "WARNING",
                )
        else:
            pass
    return new_user_input, info


def select_input_file(user_input, debug=False):
    """
    \nThis function asks the user to select the input file.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    """

    new_user_input = user_input.copy()
    if check_key(user_input, "input_file") == False:
        file_names = [
            file_name.split(".")[0] for file_name in os.listdir(f"{root}/config/input")
        ]
        q = [
            inquirer.List(
                "input_file",
                message=" select input file [flag: -i]",
                choices=file_names,
                default="TUTORIAL",
            )
        ]
        new_user_input["input_file"] = [inquirer.prompt(q)["input_file"]]
    if debug:
        print_colored("Using input file %s" % new_user_input["input_file"][0], "INFO")
    return new_user_input


def use_default_input(user_input, default_dict, info, debug=False):
    """
    \nThis function updates the user input by asking the user to provide the missing information.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    \n- **info** (*dict*) - Dictionary with the information from the input file.
    """
    new_user_input = user_input.copy()
    for default_key in default_dict:
        if check_key(new_user_input, default_key) == False:
            runs = []
            if type(default_dict[default_key]):
                for key in default_dict[default_key]:
                    if check_key(info, key):
                        for run in info[key]:
                            if run not in runs:
                                runs.append(run)
                new_user_input[default_key] = runs

            if type(default_dict[default_key]) == dict:
                for key in default_dict[default_key]:
                    if check_key(info, key):
                        value = info[key][default_dict[default_key][key]]
                        new_user_input[default_key] = [value]

            if new_user_input["debug"]:
                print_colored(
                    "No %s provided. Using all %s from input file. %s"
                    % (default_key, default_key, runs),
                    "WARNING",
                )
    return new_user_input


def print_macro_info(macro, debug=False):
    f = open("info/" + macro + ".txt", "r")
    file_contents = f.read()
    print(file_contents + "\n")
    f.close
    if debug:
        print_colored("....... Debug Mode Activated! .......", "DEBUG")


def print_header():
    f = open("info/header.txt", "r")
    file_contents = f.read()
    print(file_contents)
    f.close
    print_colored("....... Starting Macro .......", "INFO")


def apply_cuts(user_input, info, debug=False):
    """
    \nThis function asks the user to select the cuts to be apply to your events.
    \n**VARIABLES:**
    \n- **user_input** (*dict*) - Dictionary with the user input.
    """
    cuts_choices = ["cut_df", "cut_lin_rel", "cut_peak_finder"]
    cut_dict = cuts_info2dict(user_input, info, debug=True)
    for cut in cuts_choices:
        if cut_dict[cut][0] == True:
            # if debug: print_colored("Using cuts options %s"%cut_dict,"INFO")
            return cut_dict
        if cut_dict[cut][0] == False:
            ask4cuts = True
            q = [
                inquirer.Checkbox(
                    "filter",
                    message=" select the cuts you want to apply",
                    choices=cuts_choices,
                )
            ]
            my_cuts = [inquirer.prompt(q)["filter"]][0]
            for cut in cuts_choices:
                if cut in my_cuts:
                    if cut == "cut_df":
                        while ask4cuts:
                            if cut_dict[cut][0] != True:
                                cut_dict[cut] = [True, []]
                            channels = [
                                inquirer.Text(
                                    "channels",
                                    message="Select channels for applying **%s**" % cut,
                                    default="0,1",
                                )
                            ]
                            key = [
                                inquirer.Text(
                                    "key",
                                    message="Select key for applying **%s**" % cut,
                                    default="AnaPedSTD",
                                )
                            ]
                            logic = [
                                inquirer.Text(
                                    "logic",
                                    message="Select logic for applying **%s**" % cut,
                                    default="bigger",
                                )
                            ]
                            value = [
                                inquirer.Text(
                                    "value",
                                    message="Select value for applying **%s**" % cut,
                                    default="1",
                                )
                            ]
                            inclusive = [
                                inquirer.Text(
                                    "inclusive",
                                    message="Select inclusive for applying **%s**"
                                    % cut,
                                    default="False",
                                )
                            ]
                            cut_dict[cut][1].append(
                                [
                                    inquirer.prompt(channels)["channels"].split(","),
                                    inquirer.prompt(key)["key"],
                                    inquirer.prompt(logic)["logic"],
                                    tuple(
                                        float(x)
                                        for x in inquirer.prompt(value)["value"].split(
                                            ","
                                        )
                                    ),
                                    inquirer.prompt(inclusive)["inclusive"].lower()
                                    in ["true", "1", "t", "y", "yes"],
                                ]
                            )
                            ask4cuts = input(
                                "\nDo you want to add another cut? (y/n) "
                            ).lower() in ["true", "1", "t", "y", "yes"]

                    if cut == "cut_lin_rel":
                        while ask4cuts:
                            if cut_dict[cut][0] != True:
                                cut_dict[cut] = [True, []]
                            key = [
                                inquirer.Text(
                                    "key",
                                    message="Select 2 keys for applying **%s**" % cut,
                                    default="AnaPeakAmp,AnaChargeAveRange",
                                )
                            ]
                            compare = [
                                inquirer.Text(
                                    "compare",
                                    message="NONE, RUNS, CHANNELS to decide the histogram to use",
                                    default="NONE",
                                )
                            ]
                            cut_dict[cut][1].append(
                                [
                                    inquirer.prompt(key)["key"].split(","),
                                    inquirer.prompt(compare)["compare"],
                                ]
                            )
                            ask4cuts = input(
                                "\nDo you want to add another cut? (y/n) "
                            ).lower() in ["true", "1", "t", "y", "yes"]

                    if cut == "cut_peak_finder":
                        while ask4cuts:
                            if cut_dict[cut][0] != True:
                                cut_dict[cut] = [True, []]
                            n_peaks = [
                                inquirer.Text(
                                    "n_peaks",
                                    message="Select number of peaks for applying **%s**"
                                    % cut,
                                    default="1",
                                )
                            ]
                            cut_dict[cut][1].append(
                                [inquirer.prompt(n_peaks)["n_peaks"]]
                            )
                            ask4cuts = input(
                                "\nDo you want to add another cut? (y/n) "
                            ).lower() in ["true", "1", "t", "y", "yes"]

            if debug:
                print_colored("Using cuts options %s" % cut_dict, "INFO")
            return cut_dict


def opt_selector(filename="VisConfig", debug=False):
    my_opt = read_yaml_file(filename, path=f"{root}/config/", debug=debug)
    print(my_opt)
    q = [
        inquirer.List(
            "change",
            message="Do you want to change a line? (yes/no)",
            choices=["yes", "no"],
            default="no",
        )
    ]
    change_line = inquirer.prompt(q)["change"].strip().lower()
    update_opt = dict()
    if change_line in ["yes", "y", "true", "1"]:
        q = [
            inquirer.Checkbox(
                "lines", message="Choose the lines to change", choices=my_opt.keys()
            )
        ]
        line_label = inquirer.prompt(q)["lines"]
        for line in line_label:
            options = ""
            if type(my_opt[line]) == bool:
                options = "(True/False)"
            if type(my_opt[line]) == str:
                options = ""
            if type(my_opt[line]) == list:
                options = "(comma separated list)"
            new_text = input(f"Enter new entry for line {line} {options}: ")
            update_opt[line] = new_text
        update_yaml_file(f"{root}/config/{filename}.yml", update_opt)
    my_opt = read_yaml_file(filename, path=f"{root}/config/", debug=debug)
    return my_opt


def convert_str_to_type(value, debug=False):
    try:
        value = ast.literal_eval(value)
        # If value is numpy array, convert it to list
        if type(value) == np.ndarray:
            value = value.tolist()
        if type(value) == tuple:
            value = list(value)
        return value
    except (ValueError, SyntaxError):
        return value


def update_yaml_file(
    file_path: str, new_data: dict, convert: bool = True, debug: bool = False
):
    # If file path doesn't exist, create it. Take into account that the file name is included in the path.
    if not os.path.exists(file_path):
        print(f"YAML file '{file_path}' doesn't exist. Creating it...")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Update folder permissions
        os.system(f"chmod -R 770 {os.path.dirname(file_path)}")
        with open(file_path, "w") as file:
            yaml.dump(new_data, file, default_flow_style=False, sort_keys=False)
        print(f"YAML file '{file_path}' successfully created.")
        return

    # Update YAML file
    try:
        with open(file_path, "r") as file:
            existing_data = yaml.safe_load(file)
        if convert:
            new_data = {
                key: convert_str_to_type(value) for key, value in new_data.items()
            }
        existing_data.update(new_data)
        with open(file_path, "w") as file:
            yaml.dump(existing_data, file, default_flow_style=False, sort_keys=False)
        print(f"YAML file '{file_path}' successfully updated.")

    except Exception as e:
        print(f"Error updating YAML file: {e}")
