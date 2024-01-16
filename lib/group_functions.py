import numpy as np
import inquirer
from itertools import product
from rich import print as print

def group_selector(data, remove = False, operation = "add", debug = False):
    '''
    Ask the user to select runs and/or chs to group and generate a combination dictionary
    '''
    # Ask the user to select runs and/or chs to group
    print("Select runs and/or chs to group (Type 'done' when finished)")
    combination_dict = {"NRun":[],"NChannel":[]}
    
    for selector in ["NRun","NChannel"]:
        while True:
            if type(data[selector]) == np.ndarray:
                data[selector] = data[selector].tolist()

            q1 = [ inquirer.Checkbox(selector, message=f"Choose the {selector} to group", choices=data[selector]) ]
            user_input = inquirer.prompt(q1)[selector]

            # Check if user input is empty
            if len(user_input) > 1:
                user_input = tuple(user_input)
                combination_dict[selector].append(user_input)
                print(combination_dict)
            if len(user_input) == 1:
                print("[yellow]WARINNG: You must select at least two runs/chs to group[yellow]")

            if len(user_input) == 0:
                print("No runs/chs selected")
                break
    
    # group the data
    comb_data = group_data(data, combination_dict, remove=remove, operation=operation, debug=debug)
    return comb_data

def group_data(data, combination_dict, remove = False, operation = "add", debug = False):
    '''
    group runs and/or chs in the data dictionary
    '''
    # First check that the combination dictionary has the correct structure
    if not all(key in ["NRun","NChannel"] for key in combination_dict.keys()):
        raise ValueError("The combination dictionary should have the structure combination_dict = {'runs':[(run_i,run_j,...),...],'chns':[(ch_i,ch_j,...),...]}")
    
    # Check if tuples contain strings or integers and convert to strings
    combination_dict["NRun"] = [tuple(np.asarray(run).astype(str)) for run in combination_dict["NRun"]]
    combination_dict["NChannel"] = [tuple(np.asarray(chn).astype(str)) for chn in combination_dict["NChannel"]]

    # group data
    for runs in combination_dict["NRun"]:
        data = group_runs(data, runs, remove=remove, operation=operation, debug=debug)
    for chns in combination_dict["NChannel"]:
        data = group_chns(data, chns, remove=remove, operation=operation, debug=debug)

    return data

def group_runs(data, runs: tuple, operation, remove = True, debug = False):
    '''
    group runs in the data dictionary
    '''
    # First check if the runs exist in the data dictionary
    if not all(run in data["NRun"] for run in runs):
        raise ValueError("Runs not found in data dictionary")
    
    # Make a new data dictionary
    grouped_runs = {}
    grouped_runs["NRun"] = []
    grouped_runs["NChannel"] = data["NChannel"] 
    

    new_run = "+".join(np.asarray(runs).astype(str))
    grouped_runs[new_run] = {}
    for run, ch, var in product(runs, data["NChannel"], data[data["NRun"][0]][data["NChannel"][0]].keys()):
        if ch not in grouped_runs[new_run].keys():
            grouped_runs[new_run][ch] = {}
        
        elif var not in grouped_runs[new_run][ch].keys():
            grouped_runs[new_run][ch][var] = data[run][ch][var]

        else:
            grouped_runs = group_vars(operation, data, grouped_runs, new_run, ch, var, run, debug=debug)

    grouped_runs["NRun"].append(new_run)

    for run, ch, var in product(data["NRun"], data["NChannel"], data[data["NRun"][0]][data["NChannel"][0]].keys()):
        # print(run, runs, remove)
        if run in runs and remove:
            # if debug: print("Skipping: run %s - ch %s", run, ch)
            continue
        # Check if the run already exists in the grouped_runs dictionary
        if run not in grouped_runs.keys():
            grouped_runs[run] = {}
        if ch not in grouped_runs[run].keys():
            grouped_runs[run][ch] = {}
        try: grouped_runs[run][ch][var] = data[run][ch][var]
        except KeyError: 
            grouped_runs[run][ch][var] = []
            if debug: print(f"Could not find {var} in run{run}_{ch}")
        if run not in grouped_runs["NRun"]: grouped_runs["NRun"].append(run)

    return grouped_runs


def group_chns(data, chs: tuple, operation, remove = True, debug = False):
    '''
    group chs in the data dictionary
    '''
    # First check if the chs exist in the data dictionary
    if not all(ch in data["NChannel"] for ch in chs):
        raise ValueError("chs not found in data dictionary")
    
    # Make a new data dictionary
    grouped_chns = {}
    grouped_chns["NRun"] = data["NRun"]
    grouped_chns["NChannel"] = []

    new_ch = "+".join(np.asarray(chs).astype(str))
    grouped_chns["NChannel"].append(new_ch)
    for run in data["NRun"]:
        appended_vars = []
        grouped_chns[run] = {}
        grouped_chns[run][new_ch] = {}
        for ch, var in product(chs, data[data["NRun"][0]][data["NChannel"][0]].keys()):
            if var not in appended_vars:
                try: grouped_chns[run][new_ch][var] = data[run][ch][var]
                except KeyError:
                    grouped_chns[run][new_ch][var] = []
                    if debug: print(f"Could not find {var} in run{run}_{ch}")
                appended_vars.append(var)
            else:
                grouped_chns = group_vars(operation, data, grouped_chns, run, new_ch, var, ch, debug=debug)

    for run, ch, var in product(data["NRun"], data["NChannel"], data[data["NRun"][0]][data["NChannel"][0]].keys()):
        # print(ch, chs, remove)
        if ch in chs and remove:
            # if debug: print("Skipping: run %s - ch %s", run, ch)
            continue
        # Check if the ch already exists in the grouped_chns dictionary
        if ch not in grouped_chns[run].keys():
            grouped_chns[run][ch] = {}
        try: grouped_chns[run][ch][var] = data[run][ch][var]
        except KeyError: 
            grouped_chns[run][ch][var] = []
            if debug: print(f"Could not find {var} in run{run}_{ch}")
        if ch not in grouped_chns["NChannel"]: grouped_chns["NChannel"].append(ch)
    
    return grouped_chns


def group_vars(operation, data, grouped_chns, run, new_ch, var, ch, debug=False):
    try:
        if operation == "append":
            grouped_chns[run][new_ch][var] = np.concatenate((grouped_chns[run][new_ch][var],data[run][ch][var]))
        elif operation == "add":
            grouped_chns[run][new_ch][var] = grouped_chns[run][new_ch][var] + data[run][ch][var]
        elif operation == "multiply":
            grouped_chns[run][new_ch][var] = grouped_chns[run][new_ch][var] * data[run][ch][var]
    except ValueError:
        print(f"Could not {operation} {var} arrays")
    except TypeError:
        print(f"Could not {operation} {var} arrays")
    except KeyError: 
        grouped_chns[run][new_ch][var] = []
        if debug: print(f"Could not find {var} in run{run}_{ch}")

    return grouped_chns