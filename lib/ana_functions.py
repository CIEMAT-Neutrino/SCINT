# ================================================================================================================================================#
# This library contains functions to compute variables from the raw data. They are mostky used in the *Process.py macros.                        #
# ================================================================================================================================================#

import numba
import inquirer
import numpy as np
import matplotlib.pyplot as plt

from itertools import product
from scipy.signal import find_peaks
from rich import print as print

# Import from other libraries
from .io_functions import print_colored, check_key

# ===========================================================================#
# ************************* PEAK + PEDESTAL *********************************#
# ===========================================================================#


def compute_ana_wvfs(
    my_runs: dict, info: dict, filter: bool = False, debug: bool = False
):
    """
    \nComputes the AnaADC wvfs from the RawADC and the baseline value computed from PED_KEY.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data.
    \n**- info**:    dictionary containing the info.
    \n**- debug**:   boolean to print debug messages.
    """
    for run, ch in product(
        np.array(my_runs["NRun"]).astype(str), np.array(my_runs["NChannel"]).astype(str)
    ):
        if check_key(my_runs[run][ch], "RawADC") == False:
            print("[red]ERROR: RawADC not found! Please run 00Raw2Npy.py [/red]")
            return False
        if check_key(my_runs[run][ch], "Raw" + info["PED_KEY"][0]) == False:
            print(
                f"[red]ERROR: Raw {info['PED_KEY'][0]} not found! Please run 01PreProcess.py[/red]"
            )
            return False
        my_runs[run][ch]["AnaADC"] = (
            my_runs[run][ch]["PChannel"]
            * (
                my_runs[run][ch]["RawADC"].T
                - my_runs[run][ch]["Raw" + info["PED_KEY"][0]]
            ).T
        )
        if filter:
            # Apply filter to the wvfs
            filter_array = np.array(
                len(my_runs[run][ch]["AnaADC"]),
                len(my_runs[run][ch]["AnaADC"][0]),
                dtype=np.float32,
            )
            for idx, wvf in enumerate(my_runs[run][ch]["AnaADC"]):
                filter_array[idx] = filter_wvf(wvf)
            my_runs[run][ch]["AnaADC"] = filter_array

    print("[green]--> Computed AnaADC Wvfs!!![/green]")
    return True


@numba.njit
def filter_wvf(wvf):
    error = 0
    filtered_array = np.zeros(len(wvf), dtype=np.float32)
    for jdx, j in enumerate(wvf):
        if jdx < 1:
            error = 0
            filtered_array[jdx] = j
        else:
            error = 1 / 4 * (j - filtered_array[jdx - 1])
            filtered_array[jdx] = filtered_array[jdx - 1] + error
    return filtered_array


def compute_fft_wvfs(
    my_runs: dict, info: dict, key: str, label: str, debug: bool = False
):
    """
    \nComputes the FFT wvfs from the given ADC key.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data.
    \n**- info**:    dictionary containing the info.
    \n**- key**:     key to be inserted.
    \n**- label**:   label to be inserted.
    \n**- debug**:   boolean to print debug messages.
    """
    for run, ch in product(
        np.array(my_runs["NRun"]).astype(str), np.array(my_runs["NChannel"]).astype(str)
    ):
        my_runs[run][ch][label + "FFT"] = np.abs(np.fft.rfft(my_runs[run][ch][key]))
        my_runs[run][ch][label + "Freq"] = [
            np.fft.rfftfreq(
                my_runs[run][ch][key][0].size, d=my_runs[run][ch]["Sampling"]
            )
        ]
        my_runs[run][ch][label + "MeanFFT"] = [
            np.mean(my_runs[run][ch][label + "FFT"], axis=0)
        ]
        print(
            f"[green]FFT wvfs have been computed for run {run} ch {ch}[/green]",
        )
    print(f"[green]--> Computed AnaFFT Wvfs!!![/green]")


def compute_peak_variables(
    my_runs: dict,
    info: dict,
    key: str,
    label: str,
    buffer: int = 30,
    debug: bool = False,
):
    """
    \nComputes the peaktime and amplitude for a given ADC key.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data.
    \n**- info**:    dictionary containing the info.
    \n**- key**:     key to be inserted.
    \n**- label**:   label to be inserted.
    \n**- buffer**:  size in bins of the buffer to compute the valley amplitude
    \n**- debug**:   boolean to print debug messages.
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        aux_ADC = my_runs[run][ch][key]
        if key == "RawADC" and label == "Raw":
            my_runs[run][ch][label + "PeakAmp"] = my_runs[run][ch]["PChannel"] * np.max(
                my_runs[run][ch]["PChannel"] * aux_ADC[:, :], axis=1
            )
            my_runs[run][ch][label + "PeakTime"] = np.argmax(
                my_runs[run][ch]["PChannel"] * aux_ADC[:, :], axis=1
            )

            # Compute valley amplitude in the buffer around the peak to avoid noise
            i_idx = my_runs[run][ch][label + "PeakTime"]
            i_idx[i_idx < 0] = 0
            this_aux_ADC = shift_ADCs(aux_ADC, -i_idx, debug=debug)

            my_runs[run][ch][label + "ValleyAmp"] = my_runs[run][ch]["PChannel"] * (
                np.min(my_runs[run][ch]["PChannel"] * this_aux_ADC[:, :buffer], axis=1)
            )
            my_runs[run][ch][label + "ValleyTime"] = i_idx + np.argmin(
                my_runs[run][ch]["PChannel"] * this_aux_ADC[:, :buffer], axis=1
            )

        else:
            my_runs[run][ch][label + "PeakAmp"] = np.max(aux_ADC[:, :], axis=1)
            my_runs[run][ch][label + "PeakTime"] = np.argmax(aux_ADC[:, :], axis=1)
            # Compute valley amplitude in the buffer around the peak to avoid noise
            i_idx = my_runs[run][ch][label + "PeakTime"]
            i_idx[i_idx < 0] = 0
            this_aux_ADC = shift_ADCs(aux_ADC, -i_idx, debug=debug)

            my_runs[run][ch][label + "ValleyAmp"] = np.min(
                this_aux_ADC[:, :buffer], axis=1
            )
            my_runs[run][ch][label + "ValleyTime"] = i_idx + np.argmin(
                this_aux_ADC[:, :buffer], axis=1
            )
    print_colored("--> Computed Peak Variables!!!", "SUCCESS")


def compute_pedestal_variables(
    my_runs, info, key, label, ped_lim="", buffer=50, sliding=200, debug=False
):
    """
    \nComputes the pedestal variables of a collection of a run's collection in several windows.
    \n**VARIABLES:**
    \n**- my_runs**: dictionary containing the data.
    \n**- info**:    dictionary containing the info.
    \n**- key**:     key to be inserted.
    \n**- label**:   string added to the new variables. Eg: label = Raw, variable = PedSTD --> RawPedSTD.
    \n**- ped_lim**: size in bins of the sliding window.
    \n**- buffer**:  size in bins of the buffer to compute the valley amplitude.
    \n**- sliding**: bins moved between shifts of the window.
    \n**- debug**:   boolean to print debug messages.
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if type(ped_lim) != int:
            values, counts = np.unique(
                my_runs[run][ch][label + "PeakTime"], return_counts=True
            )
            ped_lim = values[np.argmax(counts)]
            ped_mode = 0

            if ped_lim <= buffer:
                ped_lim = int(len(my_runs[run][ch][key][0]) * 0.2)
                print(
                    f"[yellow]WARNING: Peak time is smaller than {buffer}. Setting ped_lim = {ped_lim} (20% window length)[/yellow]"
                )

            if key == "RawADC" and label == "Raw":
                wvf_length = len(my_runs[run][ch][key][0])
                values, counts = np.unique(
                    my_runs[run][ch][key][:, : int(0.18 * wvf_length)],
                    return_counts=True,
                )
                ped_mode = values[np.argmax(counts)]
                if ped_mode == 0:
                    print(
                        f"[yellow]WARNING: Pedestal mode is 0. Setting ped_mode = mean of the first 18% of the waveform.[/yellow]"
                    )
                    ped_mode = np.mean(
                        my_runs[run][ch][key][:, : int(0.18 * wvf_length)], axis=1
                    )

            # Find the most likely rise time wrt the most likely peak time
            end = (my_runs[run][ch][key][:, ped_lim:] - ped_mode) < 0
            start = (my_runs[run][ch][key][:, :ped_lim] - ped_mode) < 0
            if label == "Raw" and my_runs[run][ch]["PChannel"] == -1:
                my_runs[run][ch][label + "SignalEnd"] = ped_lim + np.argmin(end, axis=1)
                my_runs[run][ch][label + "SignalStart"] = ped_lim - np.argmin(
                    start[:, ::-1], axis=1
                )
                print(
                    f"[cyan]INFO: Negative polarity. Finding signal start and end in negative values.[/cyan]"
                )
            else:
                my_runs[run][ch][label + "SignalEnd"] = ped_lim + np.argmax(end, axis=1)
                my_runs[run][ch][label + "SignalStart"] = ped_lim - np.argmax(
                    start[:, ::-1], axis=1
                )

            # Look for max counts in the signal start for values up to ped_lim - buffer
            min_signal_start = np.min(my_runs[run][ch][label + "SignalStart"])
            max_signal_start = np.max(my_runs[run][ch][label + "SignalStart"])
            hist, bins = np.histogram(
                my_runs[run][ch][label + "SignalStart"],
                bins=np.arange(min_signal_start, max_signal_start + 1),
            )
            bins = bins[:-1]
            hist = hist / np.max(hist)
            # Apply peak finder to the histogram
            peaks, _ = find_peaks(hist, prominence=0.1, height=0.1)

            if len(peaks) == 0:
                print(
                    f"[yellow]WARNING:[/yellow] No peak found in the 'SignalStart' histogram. Starting peak search with lower threshold."
                )
                lower_thld = 0.1
                while len(peaks) == 0 or lower_thld >= 0.01:
                    lower_thld -= 0.001
                    peaks, _ = find_peaks(
                        hist, prominence=lower_thld, height=lower_thld
                    )
                    if lower_thld < 0:
                        print(f"[red]ERROR:[/red] No peak found in the 'SignalStart' histogram for any threshold. Exiting.")
                        break

            elif len(peaks) == 1:
                ped_lim = bins[peaks[0]]
                print(f"[cyan]INFO: Setting ped_lim = {ped_lim}[/cyan]")

            elif len(peaks) > 1:
                print(
                    f"[yellow]WARNING: Found more than one peak in the signal start histogram.[/yellow]"
                )
                # Plot the histogram and the peaks
                plt.ion()
                plt.plot(bins, hist)
                plt.plot(bins[peaks], hist[peaks], "x")
                plt.title(f"Signal Start Histogram for Run {run} Ch {ch}")
                plt.xlabel("Signal Start (ticks)")
                plt.ylabel("Norm.")
                plt.show()
                while not plt.waitforbuttonpress(-1):
                    pass
                plt.close()
                plt.ioff()

                # Select in the terminal the peak to use (defailt is the first one)
                questions = [
                    inquirer.List(
                        "peak",
                        message="Select the peak to use as signal start",
                        choices=[str(i) for i in bins[peaks]],
                    )
                ]
                answers = inquirer.prompt(questions)
                ped_lim = bins[int(answers["peak"])]

            if ped_lim <= buffer:
                ped_lim = int(len(my_runs[run][ch][key][0]) * 0.15)
                print(
                    f"[yellow]WARNING: Peak time is smaller than {buffer}. Setting ped_lim = {ped_lim} (15% window length)[/yellow]"
                )

        ADC_aux = my_runs[run][ch][key]
        my_runs[run][ch][label + "PreTriggerSTD"] = np.std(ADC_aux[:, :ped_lim], axis=1)
        my_runs[run][ch][label + "PreTriggerMean"] = np.mean(
            ADC_aux[:, :ped_lim], axis=1
        )
        my_runs[run][ch][label + "PreTriggerMax"] = np.max(ADC_aux[:, :ped_lim], axis=1)
        my_runs[run][ch][label + "PreTriggerMin"] = np.min(ADC_aux[:, :ped_lim], axis=1)

        ADC, start_window = compute_pedestal_sliding_windows(
            ADC_aux, ped_lim=ped_lim, sliding=sliding
        )
        my_runs[run][ch][label + "PedLim"] = ped_lim
        my_runs[run][ch][label + "PedSTD"] = np.std(ADC[:, :sliding], axis=1)
        my_runs[run][ch][label + "PedMean"] = np.mean(ADC[:, :sliding], axis=1)
        my_runs[run][ch][label + "PedMax"] = np.max(ADC[:, :sliding], axis=1)
        my_runs[run][ch][label + "PedMin"] = np.min(ADC[:, :sliding], axis=1)
        my_runs[run][ch][label + "PedStart"] = start_window
        my_runs[run][ch][label + "PedEnd"] = start_window + sliding
    print_colored("--> Computed Pedestal Variables!!!", "SUCCESS")


def compute_wvf_variables(my_runs, info, key, label, debug=False):
    """
    \nComputes the mean, std and rms of the given ADC key.
    \n**VARIABLES:**
    \n**- my_runs**: dictionary containing the data.
    \n**- info**:    dictionary containing the info.
    \n**- key**:     key to be inserted.
    \n**- label**:   string added to the new variables. Eg: label = Raw, variable = PedSTD --> RawPedSTD.
    \n**- debug**:   boolean to print debug messages.
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        my_runs[run][ch][label + "Mean"] = np.mean(my_runs[run][ch][key], axis=1)
        my_runs[run][ch][label + "STD"] = np.std(my_runs[run][ch][key], axis=1)
        my_runs[run][ch][label + "RMS"] = np.sqrt(
            np.mean(
                np.power(
                    (my_runs[run][ch][key].T - my_runs[run][ch][label + "Mean"]).T, 2
                ),
                axis=1,
            )
        )
    print_colored("--> Computed Wvf Variables!!!", "SUCCESS")


def compute_pedestal_sliding_windows(ADC, ped_lim, sliding=200, debug=False):
    """
    \nTaking the best between different windows in pretrigger. Same variables than "compute_pedestal_variables_sliding_window".
    It checks for the best window.
    \n**VARIABLES:**
    \n**- ADC**:      array containing the ADCs.
    \n**- ped_lim**:  size in bins of the sliding window.
    \n**- sliding**:  bins moved between shifts of the window.
    \n**- debug**:    boolean to print debug messages.
    """
    if ped_lim < sliding:
        ped_lim = sliding
        print_colored(
            "WARNING: Pedestal window is smaller than sliding window. Setting ped_lim = %s"
            % sliding,
            "WARNING",
        )

    slides = int(ped_lim / sliding)
    nwvfs = ADC.shape[0]
    aux = np.zeros((nwvfs, slides))

    for i in range(slides):
        aux[:, i] = np.std(ADC[:, (i * sliding) : ((i + 1) * sliding)], axis=1)
    try:
        start_window = np.argmin(aux, axis=1) * sliding
    except ValueError:
        print_colored(
            "ERROR: There is a problem with the pedestal computation. Check the data!",
            "ERROR",
        )
        start_window = np.zeros(nwvfs)

    ADC_s = shift_ADCs(ADC, (-1) * start_window)

    if debug:
        print_colored(
            "Calculating pedestal variables from sliding window of %i bins" % (sliding),
            "INFO",
        )
    return ADC_s, start_window


def compute_power_spec(ADC, timebin, debug=False):
    """
    \nComputes the power spectrum of the given events. It returns both axis.
    \n**VARIABLES**:
    \n**- ADC**:     array containing the ADCs.
    \n**- timebin**: timebin of the data.
    \n**- debug**:   boolean to print debug messages.
    """
    aux = []
    aux_X = np.fft.rfftfreq(len(ADC[0]), timebin)
    for i in range(len(ADC)):
        aux.append(np.fft.rfft(ADC[i]))

    return np.absolute(np.mean(aux, axis=0)), np.absolute(aux_X)


@numba.njit
def shift_ADCs(ADC, shift, debug=False):
    """
    \nUsed for the sliding window.
    \n**VARIABLES**:
    \n**- ADC**:   array containing the ADCs.
    \n**- shift**: array containing the shift values.
    \n**- debug**: boolean to print debug messages.
    """
    N_wvfs = ADC.shape[0]
    aux_ADC = np.zeros(ADC.shape)
    for i in range(N_wvfs):
        aux_ADC[i] = shift4_numba(ADC[i], int(shift[i]))  # Shift the wvfs
    return aux_ADC


# eficient shifter (c/fortran compiled); https://stackoverflow.com/questions/30399534/shift-elements-in-a-numpy-array
@numba.njit
def shift4_numba(
    arr, num, fill_value=0, debug=False
):  # default shifted value is 0, remember to always substract your pedestal first
    """
    \nUsed for the sliding window.
    \n**VARIABLES**:
    \n**- arr**:        array to be shifted.
    \n**- num**:        number of bins to be shifted.
    \n**- fill_value**: value to be inserted in the empty bins.
    \n**- debug**:      boolean to print debug messages.
    """
    if num > 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:
        return arr


# ===========================================================================#
# ************************ GENERAL FUNCTIONS ********************************#
# ===========================================================================#


def insert_variable(my_runs, var, key, debug=False):
    """
    \nInsert values for each type of signal.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data
    \n**- var**:     array of values to be inserted
    \n**- key**:     key to be inserted
    \n**- debug**:   boolean to print debug messages
    """
    for run, ch in product(
        np.array(my_runs["NRun"]).astype(str), np.array(my_runs["NChannel"]).astype(str)
    ):
        i = np.where(np.array(my_runs["NRun"]).astype(str) == run)[0][0]
        j = np.where(np.array(my_runs["NChannel"]).astype(str) == ch)[0][0]

        try:
            my_runs[run][ch][key] = var[j]
        except KeyError:
            if debug:
                print_colored("Inserting value...", "DEBUG")


def get_ADC_key(my_runs, key, debug=False):
    """
    \nThis function returns the ADC key for a given run.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data
    \n**- key**:     key to be inserted
    \n**- debug**:   boolean to print debug messages
    """
    found_duplicate = 0
    if key == "":
        for this_key in my_runs[my_runs["NRun"][0]][my_runs["NChannel"][0]].keys():
            if "ADC" in this_key:
                key = this_key
                label = this_key.split("ADC")[0]
                found_duplicate += 1
                if debug:
                    print_colored("Found ADC branch: %s" % key, "DEBUG")
                if found_duplicate > 1:
                    print_colored(
                        "ERROR: Found more than one ADC key! Please check load preset.",
                        "ERROR",
                    )
                    exit()
        if found_duplicate == 0:
            print_colored("WARNING: No ADC branch found!", "WARNING")
            label = ""
        if debug:
            print_colored(
                "--> Returning key: '%s' and label: '%s'!!!" % (key, label), "SUCCESS"
            )

    else:
        label = key.split("ADC")[0]
        if debug:
            print_colored("Returning label from provided key:", "DEBUG")

    return key, label


def get_wvf_label(my_runs, key, label, debug=False):
    """
    \nThis function returns the label for a given run. This depends on the found ADC key or the one provided by the user.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data
    \n**- key**:     key to be inserted
    \n**- label**:   label to be inserted
    \n**- debug**:   boolean to print debug messages
    """
    if key == "" and label == "":
        found_key, found_label = get_ADC_key(my_runs, key, debug=debug)
        out_key = found_key
        out_label = found_label

    elif key == "" and label != "":
        found_key, found_label = get_ADC_key(my_runs, key, debug=debug)
        out_key = found_key

        if found_label != label:
            if debug:
                print_colored(
                    "WARNING: Provided label does not match found label!", "WARNING"
                )
            user_confirmation = input(
                "Do you want to continue with coustom selection? [y/n]: "
            )
            if user_confirmation.lower() in ["y", "yes"]:
                out_label = found_label
                if debug:
                    print_colored("Selected label %s" % label, "DEBUG")
            else:
                out_label = label
                if debug:
                    print_colored("Found label %s" % found_label, "DEBUG")
        else:
            out_label = found_label
            if debug:
                print_colored("Found label %s" % label, "DEBUG")

    elif key != "" and label == "":
        if debug:
            print_colored(
                "WARNING: Selected input ADC but no label provided!", "WARNING"
            )
        found_key, found_label = get_ADC_key(my_runs, key, debug=debug)
        out_key = found_key
        out_label = found_label
        if found_label != key.split("ADC")[0]:
            print_colored(
                "ERROR: Found label does not match label from provided key!", "ERROR"
            )
            exit()

    else:
        if debug:
            print_colored(
                "WARNING: Using full coustom mode for label and ADC key selection!",
                "WARNING",
            )
        out_key = key
        out_label = label

    return out_key, out_label


def generate_cut_array(my_runs, ref="", debug=False):
    """
    \nThis function generates an array of bool = True. If cuts are applied and then you run this function, it resets the cuts.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data
    \n**- ref**:     reference variable to generate the cut array
    \n**- debug**:   boolean to print debug messages
    """
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        try:
            if debug:
                print("Check cut array ref: ", my_runs[run][ch][ref])
            my_runs[run][ch]["MyCuts"] = np.ones(len(my_runs[run][ch][ref]), dtype=bool)

        except KeyError:
            if debug:
                print_colored(
                    "Reference variable for cut array generation not found!", "DEBUG"
                )
            for key in my_runs[run][ch].keys():
                try:
                    if len(my_runs[run][ch][key]) > 1:
                        if debug:
                            print_colored(
                                "Found viable reference variable: " + key, "DEBUG"
                            )
                        my_runs[run][ch]["MyCuts"] = np.ones(
                            len(my_runs[run][ch][key]), dtype=bool
                        )
                        break
                except TypeError:
                    if debug:
                        print_colored("Key " + key + " is not a numpy array", "DEBUG")
                    pass
                except KeyError:
                    if debug:
                        print_colored("Key " + key + " does not exist", "DEBUG")
                    pass
    return my_runs


def get_run_units(my_runs, debug=False):
    """
    \nComputes and store in a dictionary the units of each variable.
    \n**VARIABLES**:
    \n**- my_runs**: dictionary containing the data
    \n**- debug**:   boolean to print debug messages
    """
    if debug:
        print("Getting units...")
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        keys = my_runs[run][ch].keys()
        aux_dict = {}
        for key in keys:
            aux_dict[key] = get_unit(key, debug)
        my_runs[run][ch]["UnitsDict"] = aux_dict


def get_unit(key, debug=False):
    unit = "a.u."
    if "Amp" in key or "Ped" in key or "ADC" in key or "PreTrigger" in key:
        unit = "ADC"
    if "Time" in key or "Sampling" in key:
        unit = "ticks"
    if "Charge" in key and "Ana" in key and "PE" not in key:
        unit = "ADC x ticks"
    if "PE" in key and "Ana" in key:
        unit = "PE"
    if "Charge" in key and "Gauss" in key:
        unit = "PE"

    return unit
