import sys, inquirer, os, yaml, ast

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from typing import Optional
from rich import print as rprint
from srcs.utils import get_project_root
from .io_functions import (
    check_key,
    read_input_file,
    read_yaml_file,
    cuts_info2dict,
)

root = get_project_root()


def get_flag_dict():
    """This function returns a dictionary with the available flags for the macro.

    :params None:

    :returns: flag_dict (dict) -- Dictionary with the available flags for the macro.
    :rtype: dict
    """

    flag_dict = {
        ("-c", "--channels"): "channels \t(optional)",
        ("-d", "--debug"): "debug \t(True/False)",
        ("-e", "--export"): "export \t(True/False)",
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
    macro, input_list: Optional[list] = ["input_file", "debug"], default_dict: Optional[dict] = None, debug: bool = False
):
    """This function initializes the macro by reading the input file and the user input.
    
    :param macro: Name of the macro to be executed.
    :type macro: str
    :param input_list: List with the keys of the user input that need to be updated, defaults to ["input_file", "debug"]
    :type input_list: list, optional
    :param default_dict: Dictionary with the default values for the user input, defaults to None
    :type default_dict: dict, optional
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: user_input, info -- Dictionary with the user input and dictionary with the information from the input file.
    :rtype: tuple
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
                    rprint("[white,bold]Usage: python3 %s.py -i config_file *--flags[/white,bold]" % macro)
                    rprint("[cyan]Available Flags:[/cyan]")
                    for flag in flag_dict:
                        rprint("[cyan]%s: %s[/cyan]" % (flag[0], flag_dict[flag]))
                    exit()

            for flag in flag_dict:
                if arg == flag[0] or arg == flag[1]:
                    try:
                        user_input[flag[1].split("--")[1]] = sys.argv[
                            sys.argv.index(arg) + 1
                        ].split(",")
                        rprint(
                            "[cyan]Using %s from command line %s[/cyan]"
                            % (
                                flag_dict[flag],
                                sys.argv[sys.argv.index(arg) + 1].split(","),
                            )
                        )
                    except IndexError:
                        rprint("Provide argument for flag %s" % flag_dict[flag])
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
            rprint("WARNING: No %s flag provided --> Using False as default." % flag)
    user_input = use_default_input(user_input, default_dict, info, debug=debug)

    if debug:
        rprint("[cyan]\nUser input:[/cyan]")
        rprint(user_input)
    return user_input, info


def update_user_input(user_input, new_input_list, info, debug=False):
    """This function updates the user input by asking the user to provide the missing information.
    
    :param user_input: Dictionary with the user input.
    :type user_input: dict
    :param new_input_list: List with the keys of the user input that need to be updated.
    :type new_input_list: list
    :param info: Dictionary with the information from the input file.
    :type info: dict
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: new_user_input, info -- Dictionary with the updated user input and dictionary with the information from the input file.
    :rtype: tuple
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
        "export": "n",
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
        "export": "-e",
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
                # rprint("Using %s from user input %s"%(key_label,new_user_input[key_label]),"WARNING")
            else:
                new_user_input["filter"] = apply_cuts(user_input, info, debug=debug)
                rprint(
                    f"[yellow][WARNING] Using {key_label} from user input {new_user_input[key_label]}[/yellow]"
                )
        else:
            pass
        
    return new_user_input, info


def select_input_file(user_input, debug=False):
    """This function asks the user to select the input file.
    
    :param user_input: Dictionary with the user input.
    :type user_input: dict
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: new_user_input -- Dictionary with the updated user input.
    :rtype: dict
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
        rprint("[cyan]Using input file %s[/cyan]" % new_user_input["input_file"][0])
        
    return new_user_input


def use_default_input(user_input, default_dict, info, debug=False):
    """This function updates the user input by asking the user to provide the missing information.
    
    :param user_input: Dictionary with the user input.
    :type user_input: dict
    :param default_dict: Dictionary with the default values for the user input.
    :type default_dict: dict
    :param info: Dictionary with the information from the input file.
    :type info: dict
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: new_user_input -- Dictionary with the updated user input.
    :rtype: dict
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
                rprint(
                    "[yellow]No %s provided. Using all %s from input file. %s[/yellow]"
                    % (default_key, default_key, runs)
                )
                
    return new_user_input


def print_macro_info(macro, debug=False):
    """This function prints the information about the macro.
    
    :param macro: Name of the macro to be executed
    :type macro: str
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    """
    
    f = open("info/" + macro + ".txt", "r")
    file_contents = f.read()
    rprint(file_contents + "\n")
    f.close
    if debug:
        rprint("[magenta]....... Debug Mode Activated! .......[/magenta]")


def print_header():
    """This function prints the header of the macro.
    """
    
    f = open("info/header.txt", "r")
    file_contents = f.read()
    rprint(file_contents)
    f.close
    rprint(f"\n[cyan]....... Starting Macro .......[/cyan]")


def apply_cuts(user_input, info, debug=False):
    """This function asks the user to select the cuts to be apply to your events.
    
    :param user_input: Dictionary with the user input.
    :type user_input: dict
    :param info: Dictionary with the information from the input file.
    :type info: dict
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: cut_dict -- Dictionary with the cuts to be applied to your events.
    :rtype: dict
    """

    cuts_choices = ["cut_df", "cut_lin_rel", "cut_peak_finder"]
    cut_dict = cuts_info2dict(user_input, info, debug=True)
    for cut in cuts_choices:
        if cut_dict[cut][0] == True:
            # if debug: rprint("[cyan]Using cuts options %s[/cyan]"%cut_dict)
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
                rprint("[cyan]Using cuts options %s[/cyan]" % cut_dict)
                
            return cut_dict


def opt_selector(filename: str = "options", arguments: Optional[list] = None, debug: bool = False):
    """This function reads the options from a YAML file and allows the user to select the options to be used.
    
    :param filename: Name of the YAML file, defaults to "options"
    :type filename: str, optional
    :param arguments: List with the arguments to be used, defaults to None
    :type arguments: list, optional
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: updated_opt -- Dictionary with the updated options.
    :rtype: dict
    """
    
    my_opt = read_yaml_file(filename, path=f"{root}/config/", debug=debug)
    if arguments is None:
        new_opt = my_opt.copy()
        rprint(my_opt)
    
    elif isinstance(arguments, list) and len(arguments) == 0:
        rprint(f"[cyan][INFO] No arguments provided. Returning all options from {filename}.yml[/cyan]")
        return my_opt
    
    else:
        new_opt = dict()
        for arg in arguments:
            if arg in my_opt.keys():
                new_opt[arg] = my_opt[arg]
        rprint(new_opt)
    q = [
        inquirer.List(
            "change",
            message="Do you want to change a line? (yes/no)",
            choices=["yes", "no"],
            default="no",
        )
    ]
    change_line = inquirer.prompt(q)["change"].strip().lower()
    
    if change_line in ["yes", "y", "true", "1"]:
        q = [
            inquirer.Checkbox(
                "lines", message="Choose the lines to change", choices=new_opt.keys()
            )
        ]
        line_label = inquirer.prompt(q)["lines"]
        for line in line_label:
            options = ""
            if type(new_opt[line]) == bool:
                options = "(True/False)"
            if type(new_opt[line]) == str:
                options = ""
            if type(new_opt[line]) == list:
                options = "(comma separated list)"
            new_text = input(f"Enter new entry for line {line} {options}: ")
            new_opt[line] = new_text
        update_yaml_file(f"{root}/config/{filename}.yml", new_opt)
    
    updated_opt = read_yaml_file(filename, path=f"{root}/config/", debug=debug)
    return updated_opt


def convert_str_to_type(value, debug=False):
    """This function converts a string to its corresponding type.
    
    :param value: Value to be converted.
    :type value: str
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: value -- Converted value.
    :rtype: any
    """
    
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
    """This function updates a YAML file with new data.
    
    :param file_path: Path to the YAML file.
    :type file_path: str
    :param new_data: Dictionary with the new data to be added.
    :type new_data: dict
    :param convert: Convert string to type, defaults to True
    :type convert: bool, optional
    :param debug: Debug mode, defaults to False
    :type debug: bool, optional
    
    :return: None
    """
    # If file path doesn't exist, create it. Take into account that the file name is included in the path.
    if not os.path.exists(file_path):
        rprint(f"YAML file '{file_path}' doesn't exist. Creating it...")
        os.makedirs(os.path.dirname(file_path), mode=0o777, exist_ok=True)
        # Update folder permissions
        os.system(f"chmod -R 770 {os.path.dirname(file_path)}")
        with open(file_path, "w") as file:
            yaml.dump(new_data, file, default_flow_style=False, sort_keys=False)
        rprint(f"YAML file '{file_path}' successfully created.")
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
        rprint(f"YAML file '{file_path}' successfully updated.")

    except Exception as e:
        rprint(f"Error updating YAML file: {e}")
