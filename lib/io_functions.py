# ================================================================================================================================================#
# This library contains general functions used to read/write files, load/save data, etc.                                                         #
# ================================================================================================================================================#
from srcs.utils import get_project_root

import os, gc, uproot, copy, stat, yaml, glob

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd
from itertools import product
from rich import print as rprint

root = get_project_root()

# ===========================================================================#
# ************************** INPUT FILE *************************************#
# ===========================================================================#


# TRYING TO USE YAML INSTEAD OF TXT
def read_yaml_file(input: str, path: str=f"{root}/config/input/", debug: bool=False) -> dict:
    """Obtain the information stored in a .yml input file to load the runs and channels needed.
    
    :param input: name of the input file
    :type input: str 
    :param path: path to the input file, defaults to f"{root}/config/input/"
    :type path: str
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: data
    :rtype: dict
    """

    # Check if file exists
    if glob.glob(path + input + ".yml") == []:
        rprint(f"[red][ERROR] {input} file not found![/red]")
        raise ValueError("Input file not found!")
    
    else:
        rprint(f"\nReading input file: {input}.yml\n")
    
        with open(str(path + input) + ".yml", "r") as file:
            data = yaml.safe_load(file)
        data["NAME"] = input

        for paths in ["RAW_PATH", "NPY_PATH", "OUT_PATH"]:
            # If data[paths] exists, expand the variables
            if paths in data:
                for i, path in enumerate(data[paths]):
                    data[paths][i] = os.path.expandvars(data[paths][i])
        
        return data


def read_input_file(
    input: str,
    NUMBERS=[],
    DOUBLES=[],
    STRINGS=[],
    BOOLEAN=[],
    path: str=f"{root}/config/input/",
    debug: bool=False,
) -> dict:
    """Obtain the information stored in a .txt input file to load the runs and channels needed.
    
    :param input: name of the input file
    :type input: str
    :param NUMBERS: list of variables that are expected to be integers, defaults to []
    :type NUMBERS: list, optional
    :param DOUBLES: list of variables that are expected to be floats, defaults to []
    :type DOUBLES: list, optional
    :param STRINGS: list of variables that are expected to be strings, defaults to []
    :type STRINGS: list, optional
    :param BOOLEAN: list of variables that are expected to be booleans, defaults to []
    :type BOOLEAN: list, optional
    :param path: path to the input file, defaults to f"{root}/config/input/"
    :type path: str, optional
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: info
    :rtype: dict
    """
    
    if debug:
        rprint("[magenta]\nReading input file: " + str(input) + ".txt[/magenta]\n")
    # Using readlines()
    # Check if file is .txt or .yml
    if glob.glob(path + input + ".txt") != []:
        file = open(path + input + ".txt", "r")
        lines = file.readlines()
        info = dict()
        info["NAME"] = [input]
        if NUMBERS == []:
            NUMBERS = ["BITS", "DYNAMIC_RANGE", "CHAN_POLAR", "CHAN_AMPLI","CHAN_PED_LIM", "SIPM_PULSE", "WINDOW_SIPM_PULSE", "CELL_PULSE", "WINDOW_CELL_PULSE"]
        if DOUBLES == []:
            DOUBLES = ["SAMPLING", "I_RANGE", "F_RANGE"]
        if STRINGS == []:
            STRINGS = [
                "MUONS_RUNS",
                "LIGHT_RUNS",
                "ALPHA_RUNS",
                "CALIB_RUNS",
                "NOISE_RUNS",
                "CHAN_TOTAL",
                "DAQ",
                "MODEL",
                "RAW_PATH",
                "NPY_PATH",
                "OUT_PATH",
                "RAW_DATA",
                "OV_LABEL",
                "CHAN_LABEL",
                "LOAD_PRESET",
                "SAVE_PRESET",
                "TYPE",
                "REF",
                "ANA_KEY",
                "PED_KEY",
            ]
        if BOOLEAN == []:
            BOOLEAN = []
        # Strips the newline character
        for line in lines:
            for LABEL in DOUBLES:
                if line.startswith(LABEL):
                    try:
                        info[LABEL] = []
                        numbers = line.split(" ")[1].strip(
                            "\n"
                        )  # Takes the second element of the line
                    except IndexError:
                        if debug == True:
                            rprint(f"[yellow]{LABEL}:\nNo value found!\n[/yellow]")
                        continue

                    for i in numbers.split(","):
                        try:
                            info[LABEL].append(
                                float(i) if i != "NON" else None
                            )  # Try to convert to float and append to LABEL list
                        except ValueError:
                            if debug == True:
                                rprint(
                                    "[red]Error when reading: [/red]" + str(LABEL)
                                )
                    # if debug: rprint(str(line)+str(info[LABEL])+"\n")

            for LABEL in NUMBERS:
                if line.startswith(LABEL):
                    try:
                        info[LABEL] = []
                        numbers = line.split(" ")[1].strip(
                            "\n"
                        )  # Takes the second element of the line
                    except IndexError:
                        if debug == True:
                            rprint(f"[yellow]{LABEL}:\nNo value found!\n[/yellow]")
                        continue

                    for i in numbers.split(","):
                        try:
                            info[LABEL].append(
                                int(i) if i != "NON" else None
                            )  # Try to convert to int and append to LABEL list
                        except ValueError:
                            if debug == True:
                                rprint(
                                    "[red]Error when reading: [/red]" + str(LABEL))
                    # if debug: rprint(str(line)+str(info[LABEL])+"\n")

            for LABEL in STRINGS:
                if line.startswith(LABEL):
                    # if debug: rprint(line)
                    try:
                        info[LABEL] = []
                        numbers = line.split(" ")[1].strip(
                            "\n"
                        )  # Takes the second element of the line
                    except IndexError:
                        if debug == True:
                            rprint(f"[yellow]{LABEL}:\nNo value found!\n[/yellow]")
                        continue

                    for i in numbers.split(","):
                        try:
                            info[LABEL].append(
                                i if i != "NON" else None
                            )  # Try to append the string to LABEL list
                        except ValueError:
                            if debug == True:
                                rprint(
                                    "[red]Error when reading: [/red]" + str(LABEL))
                    # if debug: rprint(str(line)+str(info[LABEL])+"\n")
            for LABEL in BOOLEAN:
                if line.startswith(LABEL):
                    # if debug: rprint(line)
                    try:
                        info[LABEL] = []
                        numbers = line.split(" ")[1].strip(
                            "\n"
                        )  # Takes the second element of the line
                    except IndexError:
                        if debug == True:
                            rprint(f"[yellow]{LABEL}:\nNo value found!\n[/yellow]")
                        continue

                    for i in numbers.split(","):
                        try:
                            info[LABEL].append(
                                i.lower() in ["yes", "y", "true", "t", "si", "s"]
                            )  # Try to append the string to LABEL list
                        except ValueError:
                            if debug == True:
                                rprint(
                                    "[red]Error when reading: [/red]" + str(LABEL) )
                    # if debug: rprint(str(line)+str(info[LABEL])+"\n")


    elif glob.glob(path + input + ".yml") != []:
        info = read_yaml_file(input, path=path, debug=debug)

    else:
        rprint("[red]Input file not found![/red]")
        raise ValueError("Input file not found!")

    for paths in ["RAW_PATH", "NPY_PATH", "OUT_PATH"]:
        for i, path in enumerate(info[paths]):
            info[paths][i] = os.path.expandvars(info[paths][i])
    
    return info


def cuts_info2dict(user_input: dict, info: dict, debug: bool=False) -> dict:
    """Convert the information stored in the input file to a dictionary with the cuts information.
    
    :param user_input: dictionary with the user input
    :type user_input: dict
    :param info: dictionary with the information stored in the input file
    :type info: dict
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: cuts_dict
    :rtype: dict
    """
    
    cuts_dict = {
        "cut_df": [False, []],
        "cut_lin_rel": [False, []],
        "cut_peak_finder": [False, []],
    }
    keep_reading = True
    if debug:
        rprint("[magenta]Reading cuts from input file %s[/magenta]" % info["NAME"][0])
    for i, cut in enumerate(cuts_dict):
        idx = 0
        while keep_reading:
            try:
                input_list = [
                    str(idx) + "CUT_CHAN",
                    str(idx) + "CUT_TYPE",
                    str(idx) + "CUT_KEYS",
                    str(idx) + "CUT_LOGIC",
                    str(idx) + "CUT_VALUE",
                    str(idx) + "CUT_INCLUSIVE",
                ]
                info = read_input_file(
                    user_input["input_file"][0], STRINGS=input_list, debug=False
                )
                cuts_dict[cut][1].append(
                    [
                        info[str(idx) + "CUT_CHAN"],
                        info[str(idx) + "CUT_KEYS"][0],
                        info[str(idx) + "CUT_LOGIC"][0],
                        float(info[str(idx) + "CUT_VALUE"][0]),
                        info[str(idx) + "CUT_INCLUSIVE"][0].lower()
                        in ["yes", "y", "true", "t", "si", "s"],
                    ]
                )
                if cuts_dict[cut][0] == False:
                    cuts_dict[cut][0] = True
                idx += 1
                if debug:
                    rprint("[magenta]Cuts dictionary: [/magenta]" + str(cuts_dict))
            except KeyError:
                keep_reading = False
    if debug and idx == 0:
        rprint("[magenta]No cuts imported from input![/magenta]")
        
    return cuts_dict


def list_to_string(input_list: list) -> str:
    """Convert a list to a string to be written in a .txt file. Used in generate_input_file.
    
    :param input_list: list to be converted to string
    :type input_list: list
    
    :return: string
    :rtype: str
    """

    string = str(input_list).replace("[", "")
    string = string.replace("]", "")
    string = string.replace("'", "")
    string = string.replace(" ", "")

    return string


def generate_input_file(
    input_file , info, path: str=f"{root}/config/input/", label: str="", debug: bool=False
):
    """Generate a .txt file with the information needed to load the runs and channels. Used when deconvolving signals to be able to re-start the analysis workflow with the deconvolved waveforms.
    
    :param input_file: name of the input file
    :type input_file: str
    :param info: dictionary with the information stored in the input file
    :type info: dict
    :param path: path to the input file, defaults to f"{root}/config/input/"
    :type path: str, optional
    :param label: label to be added to the input file, defaults to ""
    :type label: str, optional
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """

    file = open(path + label + str(input_file[0]) + ".txt", "w+")
    for branch in info:
        if branch == "CHAN_POLAR":
            if label == "Gauss" or label == "Wiener":
                info[branch] = len(info[branch]) * [1]
        if branch == "LOAD_PRESET":
            if label == "Gauss" or label == "Wiener":
                info[branch][1] = "DEC"
                info[branch][2] = "DEC"
                info[branch][3] = "DEC"
                info[branch][4] = "DEC"
                file.write(branch + ": " + list_to_string(info[branch]) + "\n")
        if branch == "SAVE_PRESET":
            if label == "Gauss" or label == "Wiener":
                info[branch][2] = "DEC"
                file.write(branch + ": " + list_to_string(info[branch]) + "\n")
        elif branch == "ANA_KEY":
            if label == "Gauss" or label == "Wiener":
                info[branch] = label
                file.write(branch + ": " + list_to_string(info[branch]) + "\n")
        else:
            file.write(branch + ": " + list_to_string(info[branch]) + "\n")


def write_output_file(
    run,
    ch,
    output,
    filename,
    info: dict,
    header_list: list,
    write_mode: str = "w",
    not_saved: "list[int]" = [2, 3],
    debug: bool = False,
) -> bool:
    """ General function to write a txt file with the outputs obtained. The file name is defined by the given "filename" variable + _chX. If the file existed previously it appends the new fit values (it save the run for each introduced row). By default we dont save the height of the fitted gaussian in the txt.
    
    :param run: run number
    :type run: int
    :param ch: channel number
    :type ch: int
    :param output: output to be written in the file
    :type output: list
    :param filename: name of the file
    :type filename: str
    :param info: dictionary with the information stored in the input file
    :type info: dict
    :param header_list: list with the header to be written in the file
    :type header_list: list
    :param write_mode: mode to write the file, defaults to "w"
    :type write_mode: str, optional
    :param not_saved: list of columns that are not saved in the file, defaults to [2, 3]
    :type not_saved: list, optional
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: bool
    :rtype: bool
    """
    
    run = str(run).zfill(2)

    def remove_columns(flattened_data, columns_to_remove):
        return [
            [item for j, item in enumerate(row) if j not in columns_to_remove]
            for row in flattened_data
        ]

    def flatten_data_recursive(data):
        flattened = []
        for item in data:
            if isinstance(item, list):
                flattened.extend(flatten_data_recursive(item))
            else:
                flattened.append(item)
        return flattened

    def flatten_data(data):
        return [flatten_data_recursive(row) for row in data]

    folder_path = f'{root}/{info["OUT_PATH"][0]}/analysis/fits/run{run}/ch{ch}/'
    if not os.path.exists(folder_path):
        os.makedirs(name=folder_path, mode=0o777, exist_ok=True)
        os.chmod(folder_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    
    if debug:
        rprint(f"Saving in: {folder_path}run{run}_ch{ch}_{filename}.txt")

    flat_data = flatten_data(output)
    flat_data = remove_columns(flat_data, not_saved)

    confirmation = input(
        f"\nConfirmation to save in {folder_path}run{run}_ch{ch}_{filename}.txt the printed parameters (except HEIGHT) (y/n)? "
    )
    if confirmation.lower() in ["yes", "y", "true", "t", "si", "s"]:
        rprint("\n----------- Saving -----------")
        if not os.path.exists(f"{folder_path}run{run}_ch{ch}_{filename}.txt"):  # HEADER#
            os.makedirs(
                name=folder_path, mode=0o777, exist_ok=True
            )  # Create the directory if it doesnt exist
            with open(f"{folder_path}run{run}_ch{ch}_{filename}.txt", "+a") as f:
                f.write("\t".join(header_list) + "\n")  # Write the header

        with open(f"{folder_path}run{run}_ch{ch}_{filename}.txt", write_mode) as f:
            if write_mode in ["w"]:
                column_widths = [
                    max(len(str(item)) for item in col) for col in zip(*flat_data)
                ]
                try:
                    header_line = (
                        "\t".join(
                            "{{:<{}}}".format(width) for width in column_widths
                        ).format(*header_list)
                        + "\n"
                    )
                except IndexError:
                    rprint(
                        "[yellow]Header length does not match data length. Adjusting header to fit data.[/yellow]"
                    )
                    rprint(
                        f"Header length: {len(header_list)}, Data length: {len(column_widths)}"
                    )
                    header_line = (
                        "\t".join(header_list) + "\n"
                    )  # Adjust header to fit data length
                f.write(header_line)

            for i, row in enumerate(flat_data):
                data_line = (
                    "\t".join(
                        "{{:<{}}}".format(width) for width in column_widths
                    ).format(*map(str, row))
                    + "\n"
                )
                f.write(data_line)

        return True
    else:
        rprint("----------- Not saved -----------")
        return False


# ===========================================================================#
# ************************* RAW TO NUMPY ************************************#
# ===========================================================================#
def binary2npy_express(in_file: str, header_lines: int=6, debug: bool=False) -> tuple:
    """Dumper from binary format to npy tuples. Input are binary input file path and npy outputfile as strings.
    
    :param in_file: binary input file path
    :type in_file: str
    :param header_lines: number of header lines, defaults to 6
    :type header_lines: int, optional
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: ADC, TIMESTAMP
    :rtype: tuple
    """

    try:
        headers = np.fromfile(in_file, dtype="I")  # Reading .dat file as uint32
    except:
        headers = np.frombuffer(
            in_file.getbuffer(), dtype="I"
        )  # io.UnsupportedOperation: fileno --> when browsing file

    try:
        data = np.fromfile(in_file, dtype="H")  # Reading .dat file as uint16
    except:
        data = np.frombuffer(
            in_file.getbuffer(), dtype="H"
        )  # io.UnsupportedOperation: fileno --> when browsing file

    header = headers[:6]  # Read first event header
    samples = int(
        header[0] / 2 - header_lines * 2
    )  # Number of samples per event (as uint16)
    size = header_lines * 2 + samples  # Number of uint16 per event
    events = int(data.shape[0] / size)  # Number of events in the file

    ADC = np.reshape(data, (events, size))[
        :, header_lines * 2 :
    ]  # Data reshaped as (N_Events,NSamples)
    headers = np.reshape(headers, (events, int(size / 2)))[
        :, :header_lines
    ]  # Headers reshaped as (N_Events,header_lines)
    TIMESTAMP = (
        headers[:, 4] * 2**32 + headers[:, 5]
    ) * 8e-9  # Unidades TriggerTimeStamp(PC_Units) * 8e-9

    if debug:
        rprint(f"#################################")
        # rprint(f"Header:\t{header}")
        rprint(f"Ticks:\t{samples}")
        rprint(f"Events:\t{events}")
        rprint("Time:\t{:.2f}".format((TIMESTAMP[-1] - TIMESTAMP[0]) / 60) + " (min)")
        rprint("Rate:\t{:.2f}".format(events / (TIMESTAMP[-1] - TIMESTAMP[0])) + " (Hz)")
        rprint(f"#################################\n")

    return ADC, TIMESTAMP


def binary2npy(
    runs, channels, info, compressed=True, header_lines=6, force=False, debug=False
):
    """Dumper from binary format to npy tuples. Input are binary input file path and npy outputfile as strings. Depends numpy.
    
    :param runs: array with the run numbers
    :type runs: np.array
    :param channels: array with the channel numbers
    :type channels: np.array
    :param info: dictionary with the information stored in the input file
    :type info: dict
    :param compressed: if True, save the file as .npz, defaults to True
    :type compressed: bool, optional
    :param header_lines: number of header lines, defaults to 6
    :type header_lines: int, optional
    :param force: if True, overwrite the file, defaults to False
    :type force: bool, optional
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """
    
    in_path = f'{root}/{info["RAW_PATH"][0]}/'
    out_path = f'{root}/{info["NPY_PATH"][0]}/'
    # Outpath contains ${USER} but it is not recognized by the system. Force the substitution of the variable
    out_path = os.path.expandvars(out_path)

    os.makedirs(name=out_path, mode=0o777, exist_ok=True)
    for run, ch in product(runs.astype(str), channels.astype(str)):
        rprint("\n....... READING RUN%s CH%s ......." % (run, ch))
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file = (
            "run" + str(run).zfill(2) + "/wave" + str(ch) + ".dat"
        )  # Name of the input file
        out_folder = (
            "run" + str(run).zfill(2) + "/ch" + str(ch) + "/"
        )  # Name of the output folder

        try:
            os.makedirs(out_path + out_folder, mode=0o777)
        
        except FileExistsError:
            rprint("[yellow]DATA STRUCTURE ALREADY EXISTS[/yellow]")

        try:
            ADC, TIMESTAMP = binary2npy_express(
                in_path + in_file, header_lines=header_lines, debug=debug
            )
            branches = ["RawADC", "TimeStamp"]
            content = [ADC, TIMESTAMP]
            files = os.listdir(out_path + out_folder)

            for i, branch in enumerate(branches):
                try:
                    # If the file already exists and force is True, overwrite it
                    if (
                        branch + ".npz" in files or branch + ".npy" in files
                    ) and force == True:
                        rprint(
                            "[yellow]File (%s.npx) already exists. OVERWRITTEN[/yellow]" % branch
                        )
                        if compressed:  # If compressed, save .npz
                            try:
                                os.remove(
                                    out_path + out_folder + branch + ".npz"
                                )  # Remove the file if it already exists (permissions issues)
                            except FileNotFoundError:
                                rprint("[red].npy was found but not .npz[/red]")
                            np.savez_compressed(
                                out_path + out_folder + branch + ".npz", content[i]
                            )  # Save the file
                            os.chmod(
                                out_path + out_folder + branch + ".npz",
                                stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                            )  # Set permissions

                        else:  # If not compressed, save .npy
                            try:
                                os.remove(
                                    out_path + out_folder + branch + ".npy"
                                )  # Remove the file if it already exists (permissions issues)
                            except FileNotFoundError:
                                rprint("[red].npz was found but not .npy[/red]")
                            np.save(
                                out_path + out_folder + branch + ".npy", content[i]
                            )  # Save the file
                            os.chmod(
                                out_path + out_folder + branch + ".npy",
                                stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                            )  # Set permissions

                    # If file already exists, skip
                    elif branch + ".npz" in files and force == False:
                        rprint(
                            "[yellow]File (%s.npz) alredy exists.[/yellow]" % branch
                        )
                        continue

                    # If file does not exist, save it
                    else:
                        np.savez_compressed(
                            out_path + out_folder + branch + ".npz", content[i]
                        )  # Save the file
                        os.chmod(
                            out_path + out_folder + branch + ".npz",
                            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                        )  # Set permissions

                        if not compressed:
                            np.save(
                                out_path + out_folder + branch + ".npy", content[i]
                            )  # Save the file
                            os.chmod(
                                out_path + out_folder + branch + ".npy",
                                stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                            )  # Set permissions

                    if debug:
                        rprint("[magenta]%s[/magenta]"%branch)
                        rprint(
                            "[magenta]Saved data in:"
                            + str(out_path + out_folder + branch)
                            + ".npx[/magenta]"
                        )
                        rprint("[magenta]----------------------\n[/magenta]")
                    gc.collect()

                except FileNotFoundError:
                    rprint("--- File %s was not foud!!! \n" % in_file)
        # except FileNotFoundError: rprint("--- File %s was not foud!!! \n"%(in_path+in_file))
        except AttributeError:
            rprint("--- File %s does not exist!!! \n" % (in_path + in_file))


### DEPRECATED --- UPDATE ###
def root2npy(
    runs, channels, info: dict={}, debug: bool=False
):  ### ACTUALIZAR COMO LA DE BINARIO ###
    """[DEPRECATED - NEEDS UPDATE!! (see binary2npy)] Dumper from .root format to npy tuples. Input are root input file path and npy outputfile as strings. Depends on uproot, awkward and numpy. Size increases x2 times.
    
    :param runs: array with the run numbers
    :type runs: np.array
    :param channels: array with the channel numbers
    :type channels: np.array
    :param info: dictionary with the information stored in the input file
    :type info: dict
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """

    in_path = f'{root}/{info["RAW_PATH"][0]}/'
    out_path = f'{root}/{info["NPY_PATH"][0]}/'
    out_path = os.path.expandvars(out_path)

    for run, ch in product(runs.astype(str), channels.astype(str)):
        i = np.where(runs == run)[0][0]
        j = np.where(channels == ch)[0][0]

        in_file = (
            "run" + str(run).zfill(2) + "_ch" + str(ch) + ".root"
        )  # Name of the input file
        out_file = (
            "run" + str(run).zfill(2) + "_ch" + str(ch) + ".npy"
        )  # Name of the output file

        try:
            my_dict = {}
            f = uproot.open(
                in_path + in_file
            )  # Open the file and dump it in a dictionary

            if debug:
                rprint("[magenta]----------------------[/magenta]")
                rprint("[magenta]Dumping file:[/magenta]" + str(in_path + in_file))

            for branch in f["IR02"].keys():
                if debug:
                    rprint("[magenta]dumping brach:[/magenta]" + str(branch))
                my_dict[branch] = f["IR02"][branch].array().to_numpy()

            # additional useful info
            my_dict["RawADC"] = my_dict["ADC"]
            del my_dict["ADC"]
            my_dict["NBinsWvf"] = my_dict["RawADC"][0].shape[0]
            my_dict["Sampling"] = info["SAMPLING"][0]

            np.save(out_path + out_file, my_dict)

            if debug:
                rprint("[magenta]%s[/magenta]"%my_dict.keys())
                rprint("[magenta]Saved data in:[/magenta]" + str(out_path + out_file))
                rprint("[magenta]----------------------\n[/magenta]")

        except FileNotFoundError:
            rprint("--- File %s was not foud!!! \n" % in_file)


# ===========================================================================#
# ***************************** KEYS ****************************************#
# ===========================================================================#


def check_key(OPT, key) -> bool:
    """Checks if the given key is included in the dictionary OPT. Returns True if it finds the key.
    
    :param OPT: dictionary
    :type OPT: dict
    :param key: key to be checked
    :type key: str
    
    :return: bool
    """

    try:
        OPT[key]
        return True  # If the key is found, return True
    except KeyError:
        return False  # If the key is not found, return False


def delete_keys(my_runs: dict, keys: list, debug: bool=False):
    """Delete the keys list introduced as 2nd variable
    
    :param my_runs: dictionary with the runs and channels
    :type my_runs: dict
    :param keys: list with the keys to be deleted
    :type keys: list
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """

    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        try:
            del my_runs[run][ch][key]  # Delete the key
        except KeyError:
            rprint(
                "[yellow]*EXCEPTION: [Run%i - Ch%i - %s] key combination is not found in my_runs[/yellow]"
                % (run, ch, key)
            )
    if debug:
        rprint("[magenta]Keys deleted: %s[/magenta]" % keys)


# ===========================================================================#
# ************************** LOAD/SAVE NPY **********************************#
# ===========================================================================#


def get_preset_list(my_run: dict, path: str, folder: str, preset: str, option:str, debug: bool=False):
    """Return as output presets lists for load/save npy files.
    :param my_run: dictionary with the runs and channels (my_runs[run][ch])    
    :type my_run: dict
    :param path: path to the folder
    :type path: str
    :param folder: folder name
    :type folder: str
    :param preset: preset to be used (ALL, RAW, ANA, EVA, DEC, CAL, WVF)
    :type preset: str
    :param option: option to be used (LOAD, SAVE)
    :type option: str
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: branch_list
    :rtype: list
    """
    #    (a) "ALL": all the existing keys/branches
    #    (b) "ANA": only Ana keys/branches (removing RAW info)
    #    (c) "INT": only Charge*, Ave* keys/branches
    #    (d) "RAW": only Raw information i.e loaded from Raw2Np + Raw* keys
    #    (e) "EVA": all the existing keys/branches EXCEPT ADC, Dict, Cuts and Raw
    #    (f) "DEC": only DEC info i.e Wiener*, Gauss*, Dec* or Charge* keys
    #    (g) "CAL": only Charge* keys
    #    (h) "WVF": only Wvf* keys
    #    (a) "LOAD": takes the os.listdir(path+folder) as brach_list (IN)
    #    (b) "SAVE": takes the my_run.keys() as branch list (OUT)

    dict_option = dict()
    try:
        dict_option["LOAD"] = os.listdir(f"{path}{folder}")
    except FileNotFoundError:
        return None

    # Remove files that are not .npz or .npy
    dict_option["LOAD"] = [
        file
        for file in dict_option["LOAD"]
        if file.endswith(".npz") or file.endswith(".npy")
    ]
    dict_option["SAVE"] = my_run.keys()

    aux = ["TimeStamp"]
    
    branch_list = dict_option[option]
    for key in branch_list:
        if preset == "ALL":  # Save all branches
            if not "UnitsDict" in key and not "MyCuts" in key:
                aux.append(key)

        elif preset == "RAW" and option == "LOAD":  # Save aux + Raw branches
            if "Raw" in key:
                aux.append(key)

        elif preset == "RAW" and option == "SAVE":  # Save aux + Raw branches
            if "Raw" in key and "ADC" not in key:
                aux.append(key)

        elif preset == "ANA" and option == "LOAD":  # Remove Raw, Dict and Cuts branches
            if "Ana" in key or "Raw" in key:
                aux.append(key)

        elif preset == "ANA" and option == "SAVE":  # Remove Raw, Dict and Cuts branches
            if "Ana" in key and "ADC" not in key:
                aux.append(key)

        elif preset == "EVA" and option == "LOAD":  # Remove ADC, Dict and Cuts branches
            if not "ADC" in key and not "Dict" in key and not "Cuts" in key:
                aux.append(key)

        elif preset == "EVA" and option == "SAVE":  # Remove ADC, Dict and Cuts branches
            if not "ADC" in key and not "Dict" in key and not "Cuts" in key and not "Raw" in key:
                aux.append(key)

        elif preset == "DEC":  # Save aux + Gauss*, Wiener*, Dec* and Charge* branches
            if "Gauss" in key or "Wiener" in key or "Dec" in key:
                aux.append(key)

        elif preset == "CAL":  # Save aux + Charge* branches
            if "Charge" in key and key not in aux:
                aux.append(key)

        elif preset == "WVF":  # Save aux + Wvf* branches
            if "Wvf" in key and key not in aux:
                aux.append(key)

        elif preset == "SPE":  # Save aux + Wvf* branches
            if "SPE" in key or "Noise" in key and key not in aux:
                aux.append(key)
            # if "Noise" in key and key not in aux: aux.append(key)

        elif preset == "FFT":  # Save aux + Wvf* branches
            if "MeanFFT" in key or "Freq" in key and key not in aux:
                aux.append(key)

        else:
            rprint("[yellow]Preset not found. Returning all the branches.[/yellow]")
            raise ValueError("Preset not found. Returning all the branches.")

    branch_list = aux
    for branch in ["TimeStamp"]:
        if option == "SAVE":
            try:
                branch_list.remove(branch)
            except:
                rprint(f"[cyan]INFO: Branch {branch} not found in the preset list for removal[/cyan]")
                pass
    try:
        branch_list.remove("Label")
        branch_list.remove("PChannel")
        branch_list.remove("PedestalLimit")
        branch_list.remove("Sampling")
        # if option == "SAVE" remove branches in aux
    except ValueError:
        pass

    if debug:
        rprint(
            f"[bold cyan]--> Loading Variables (according to preset {preset} from {path}{folder})![/bold cyan]"
        )
        
    return branch_list


def load_npy(
    runs, channels, info, preset=None, branch_list=[], debug: bool=False, compressed: bool=True
):
    """Loads the selected channels and runs, for simplicity, all runs must have the same number of channels. Presets can be used to only load a subset of desired branches.
    
    :param runs: list of runs to load
    :type runs: list
    :param channels: list of channels to load
    :type channels: list
    :param info: dictionary with the info of the run
    :type info: dict
    :param preset: preset to be used (ALL, RAW, ANA, EVA, DEC, CAL, WVF), defaults None
    :type preset: str, optional
    :param branch_list: list of branches to load, defaults []
    :type branch_list: list
    :param debug: if True, print debug info, defaults False
    :type debug: bool
    :param compressed: if True, load the file as .npz, defaults to True
    :type compressed: bool, optional
    
    :return: my_runs with structure: run_dict[runs][channels][BRANCH]
    :rtype: dict
    """
    #    (a) "ALL": all the existing keys/branches
    #    (b) "ANA": only Ana keys/branches (removing RAW info)
    #    (c) "INT": only Charge*, Ave* keys/branches
    #    (d) "RAW": only Raw information i.e loaded from Raw2Np + Raw* keys
    #    (e) "EVA": all the existing keys/branches EXCEPT ADC
    #    (f) "DEC": only DEC info i.e Wiener*, Gauss*, Dec* or Charge* keys
    #    (g) "CAL": only Charge* keys
    
    path = f'{root}/{info["NPY_PATH"][0]}/'
    path = os.path.expandvars(path)

    nevents = 0
    my_runs = dict()
    runs = np.asarray(runs).astype(str)
    channels = np.asarray(channels).astype(str)
    my_runs["NRun"] = runs
    my_runs["NChannel"] = channels
    aux_PChannel = dict(zip(info["CHAN_TOTAL"], info["CHAN_POLAR"]))
    aux_Label = dict(zip(info["CHAN_TOTAL"], info["CHAN_LABEL"]))
    aux_Ped_Lim = dict(zip(info["CHAN_TOTAL"], info["CHAN_PED_LIM"]))

    for run in runs:
        my_runs[run] = dict()
        for ch_idx, ch in enumerate(channels):
            if debug:
                rprint(
                    f"[bold cyan]\n....... Load npy run {run} ch {ch} --> DONE! .......\n[/bold cyan]"
                )

            my_runs[run][ch] = dict()
            in_folder = "run" + str(run).zfill(2) + "/ch" + str(ch) + "/"
            if preset == None:
                rprint(
                    f"[yellow]WARNING: Preset None. Passing run {run} ch {ch}[/yellow]"
                )
                continue

            branch_list = get_preset_list(
                my_runs[run][ch], path, in_folder, preset, "LOAD", debug=debug
            )  # Get the branch list if preset is used
            # Check if brach_list is None
            if branch_list is None:
                rprint(
                    f"[yellow]WARNING: Branch list is None. Passing run {run} ch {ch}[/yellow]"
                )
                continue

            for branch in branch_list:
                if compressed:
                    try:
                        my_runs[run][ch][branch.replace(".npz", "")] = np.load(
                            path + in_folder + branch.replace(".npz", "") + ".npz",
                            allow_pickle=True,
                            mmap_mode="w+",
                        )["arr_0"]
                        if branch.__contains__("RawADC"):
                            my_runs[run][ch][branch.replace(".npz", "")] = my_runs[run][
                                ch
                            ][branch.replace(".npz", "")].astype(float)
                        try:
                            nevents = len(my_runs[run][ch][branch.replace(".npz", "")])
                        except TypeError:
                            # rprint(f"[yellow][WARNING] {branch} is not a list[/yellow]")
                            pass
                            
                    except FileNotFoundError:
                        rprint(
                            "[yellow]\nRun %s, channels %s %s --> NOT LOADED (FileNotFound)[/yellow]"
                            % (run, ch, branch)
                        )
                else:
                    try:
                        my_runs[run][ch][branch.replace(".npy", "")] = np.load(
                            path + in_folder + branch.replace(".npy", "") + ".npy",
                            allow_pickle=True,
                            mmap_mode="w+",
                        ).item()
                        if branch.__contains__("RawADC"):
                            my_runs[run][ch][branch.replace(".npy", "")] = my_runs[run][
                                ch
                            ][branch.replace(".npy", "")].astype(float)

                        try:
                            nevents = len(my_runs[run][ch][branch.replace(".npy", "")])
                        except TypeError:
                            # rprint(f"[yellow][WARNING] {branch} is not a list[/yellow]")
                            pass

                    except FileNotFoundError:
                        rprint(
                            "[yellow]\nRun %s, channels %s %s --> NOT LOADED (FileNotFound)[/yellow]"
                            % (run, ch, branch)
                        )

            my_runs[run][ch]["Label"] = aux_Label[ch]
            my_runs[run][ch]["PChannel"] = aux_PChannel[ch]
            my_runs[run][ch]["PedestalLimit"] = aux_Ped_Lim[ch]
            my_runs[run][ch]["Sampling"] = float(info["SAMPLING"][0])
            del branch_list

    my_runs["NEvents"] = nevents
    rprint(f"[bold green]--> Loaded Data Succesfully!!![/bold green]")
    
    return my_runs


def save_proccesed_variables(
    my_runs,
    info,
    preset="",
    branch_list=None,
    force=False,
    compressed=True,
    debug=False,
):
    """Saves the processed variables an npx file.
    
    :param my_runs: dictionary with the runs and channels to be saved
    :type my_runs: dict
    :param info: dictionary with the path and month to be used
    :type info: dict
    :param preset: preset to be used to save the variables
    :type preset: str
    :param branch_list: list of branches to be saved
    :type branch_list: list
    :param force: if True, the files will be overwritten, defaults to False
    :type force: bool, optional
    :param compressed: if True, the files will be saved as npz, if False, as npy, defaults to True
    :type compressed: bool, optional
    :param debug: if True, the function will print the branches that are being saved, defaults to False
    :type debug: bool
    """

    aux = copy.deepcopy(
        my_runs
    )  # Save a copy of my_runs with all modifications and remove the unwanted branches in the copy
    path = f"{root}/{info['NPY_PATH'][0]}/"
    path = os.path.expandvars(path)
    for run in aux["NRun"]:
        for ch in aux["NChannel"]:
            rprint(
                "[cyan]\n--> Saving Computed Variables (according to preset %s)![/cyan]" % (preset)
            )
            out_folder = "run" + str(run).zfill(2) + "/ch" + str(ch) + "/"
            os.makedirs(name=f"{path}{out_folder}", mode=0o777, exist_ok=True)
            files = os.listdir(f"{path}{out_folder}")
            if not branch_list:
                branch_list = get_preset_list(
                    my_runs[run][ch], path, out_folder, preset, "SAVE", debug
                )
            for key in branch_list:
                key = key.replace(".npz", "")

                # If the file already exists, skip it
                if key + ".npz" in files and force == False:
                    if debug:
                        rprint("\t[magenta]File (%s.npz) alredy exists[/magenta]" % key)
                    continue

                # If the file already exists and force is True, overwrite it
                elif (key + ".npz" in files or key + ".npy" in files) and force == True:
                    if compressed:
                        os.remove(path + out_folder + key + ".npz")
                        np.savez_compressed(
                            path + out_folder + key + ".npz", aux[run][ch][key]
                        )
                        os.chmod(
                            path + out_folder + key + ".npz",
                            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                        )
                        rprint("\t[yellow]File (%s.npz) OVERWRITTEN [/yellow]" % key)
                    else:
                        os.remove(path + out_folder + key + ".npy")
                        np.save(path + out_folder + key + ".npy", aux[run][ch][key])
                        os.chmod(
                            path + out_folder + key + ".npy",
                            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                        )
                        rprint("\t[yellow]File (%s.npy) OVERWRITTEN [/yellow]" % key)

                # If the file does not exist, create it
                elif check_key(aux[run][ch], key):
                    np.savez_compressed(
                        path + out_folder + key + ".npz", aux[run][ch][key]
                    )
                    os.chmod(
                        path + out_folder + key + ".npz",
                        stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                    )
                    rprint("[green]\tSaving NEW file: %s.npz[/green]" % key)
                    if debug:
                        rprint("\t[magenta]" + path + out_folder + key + ".npz[magenta]")
                    if not compressed:
                        np.save(path + out_folder + key + ".npy", aux[run][ch][key])
                        os.chmod(
                            path + out_folder + key + ".npy",
                            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                        )
                        rprint("\t[green]Saving NEW file: %s.npy[/green]" % key)
                        if debug:
                            rprint(
                                "\t[magenta]" + path + out_folder + key + ".npy[/magenta]"
                            )

    rprint("[green]--> Saved Data Succesfully!!![/green]")
    del my_runs


def save_figure(fig, path, run, ch, label, debug: bool=False):
    """Saves the figure in the desired path with the desired name.
    
    :param fig: figure to be saved
    :type fig: matplotlib.figure.Figure
    :param path: path to save the figure
    :type path: str
    :param run: run number
    :type run: int
    :param ch: channel number
    :type ch: int
    :param label: label of the figure
    :type label: str
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """
    
    # Ensure run has leading zeros up to 2 digits
    run = str(run).zfill(2)
    # Remove / if path ends with it
    if path[-1] == "/":
        path = path[:-1]

    os.makedirs(name=f"{path}/run{run}/ch{ch}", mode=0o777, exist_ok=True)
    # Check that fig is a matplotlib figure
    if isinstance(fig, matplotlib.figure.Figure):
        fig.savefig(f"{path}/run{run}/ch{ch}/run{run}_ch{ch}_{label}.png")
        return
    else:
        rprint(f"[red][ERROR] Input figure type {type(fig)} not implemented[/red]")
    # Give permissions to the file
    os.chmod(
        f"{path}/run{run}/ch{ch}/run{run}_ch{ch}_{label}.png",
        stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
    )
    
    if debug:
        rprint(f"Figure saved in: {path}")


def npy2root(my_runs, debug: bool=False):
    """Converts the npy files to root TTree files by converting the dictionaries to a RDataFrame from ROOT & using the snapshot method.
    
    :param my_runs: dictionary with the runs and channels to be saved
    :type my_runs: dict
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    """

    import ROOT

    # Create the ROOT dataframe
    df = ROOT.RDF.FromNumpy(my_runs)
    return df

    # Create the ROOT file
    f = ROOT.TFile.Open("test.root", "RECREATE")
    # Create the ROOT tree
    tree = df.Snapshot("tree", "test.root")
    # Save the ROOT file
    f.Write()
    f.Close()

    f2 = ROOT.TFile("test.root")
    t = f2.myTree
    rprint("These are all the columns available to this dataframe:")
    for branch in t.GetListOfBranches():
        rprint("Branch: %s" % branch.GetName())

    if debug:
        rprint("npy2root --> DONE!\n")


def npy2df(my_runs, debug: bool=False) -> pd.DataFrame:
    """Converts the npy files to a pandas dataframe.
    
    :param my_runs: dictionary with the runs and channels to be saved
    :type my_runs: dict
    :param debug: if True, print debug messages, defaults to False
    :type debug: bool
    
    :return: df
    :rtype: pd.DataFrame
    """
    
    # From my_runs.keys() remove all keys that are not a dictionary
    keys = list(my_runs.keys())
    for key in keys:
        if not isinstance(my_runs[key], dict):
            my_runs.pop(key)

    df = pd.DataFrame.from_dict(
        {(i, j): my_runs[i][j] for i in my_runs.keys() for j in my_runs[i].keys()},
        orient="index",
    )

    if debug:
        rprint("[green]npy2df --> DONE!\n[/green]")
        
    return df