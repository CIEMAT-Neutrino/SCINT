# ================================================================================================================================================#
# This library contains functions to compute variables from the raw data. They are mostky used in the *Process.py macros.                        #
# ================================================================================================================================================#

import os
import numba
import inquirer
import numpy as np
import matplotlib.pyplot as plt

from itertools import product
from scipy.signal import find_peaks
from rich import print as rprint

# Import from other libraries
from srcs.utils import get_project_root
from .io_functions import check_key
from .cut_functions import generate_cut_array
from .unit_functions import get_run_units
from .head_functions import update_yaml_file

root = get_project_root()

# ===========================================================================#
# ************************* PEAK + PEDESTAL *********************************#
# ===========================================================================#

def compute_ana_wvfs(
    my_runs: dict, info: dict, filter: bool = False, debug: bool = False
):
    """Computes the AnaADC wvfs from the RawADC and the baseline value computed from PED_KEY.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param filter: boolean to apply filter to the wvfs, defaults to False
    :type filter: bool, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: True if the computation was successful, False otherwise.
    :rtype: bool
    """

    for run, ch in product(
        np.array(my_runs["NRun"]).astype(str), np.array(my_runs["NChannel"]).astype(str)
    ):
        if check_key(my_runs[run][ch], "RawADC") == False:
            rprint("[red]ERROR: RawADC not found! Please run 00Raw2Npy.py [/red]")
            return False
        if check_key(my_runs[run][ch], "Raw" + info["PED_KEY"][0]) == False:
            rprint(
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

    rprint("[green]--> Computed AnaADC Wvfs!!![/green]")
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
    """Computes the FFT wvfs from the given ADC key.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
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
        rprint(
            f"[green]FFT wvfs have been computed for run {run} ch {ch}[/green]",
        )
    rprint(f"[green]--> Computed AnaFFT Wvfs!!![/green]")


def compute_peak_variables(
    my_runs: dict,
    info: dict,
    key: str,
    label: str,
    buffer: int = 30,
    debug: bool = False,
):
    """Computes the peaktime and amplitude for a given ADC key.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param buffer: size in bins of the buffer to compute the valley amplitude, defaults to 30
    :type buffer: int, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
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
    rprint("[green]--> Computed Peak Variables!!![/green]")


def compute_pedestal_variables(
    my_runs, info, key, label, ped_lim="", buffer=50, sliding=200, debug=False
):
    """Computes the pedestal variables of a collection of a run's collection in several windows.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted. Eg: label = Raw, variable = PedSTD --> RawPedSTD.
    :type label: str
    :param ped_lim: size in bins of the sliding window, defaults to ""
    :type ped_lim: str, optional
    :param buffer: size in bins of the buffer to compute the valley amplitude, defaults to 50
    :type buffer: int, optional
    :param sliding: bins moved between shifts of the window, defaults to 200
    :type sliding: int, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
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
                rprint(
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
                    rprint(
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
                rprint(
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
                rprint(
                    f"[yellow]WARNING:[/yellow] No peak found in the 'SignalStart' histogram. Starting peak search with lower threshold."
                )
                lower_thld = 0.1
                while len(peaks) == 0 or lower_thld >= 0.01:
                    lower_thld -= 0.001
                    peaks, _ = find_peaks(
                        hist, prominence=lower_thld, height=lower_thld
                    )
                    if lower_thld < 0:
                        rprint(f"[red]ERROR:[/red] No peak found in the 'SignalStart' histogram for any threshold. Exiting.")
                        break

            elif len(peaks) == 1:
                ped_lim = bins[peaks[0]]
                rprint(f"[cyan]INFO: Setting ped_lim = {ped_lim}[/cyan]")

            elif len(peaks) > 1:
                rprint(
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
                rprint(
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
    rprint("[green]--> Computed Pedestal Variables!!![/green]")


def compute_wvf_variables(my_runs, info, key, label, debug=False):
    """Computes the mean, std and rms of the given ADC key.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
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
    rprint("[green]--> Computed Wvf Variables!!![/green]")


def compute_pedestal_sliding_windows(ADC, ped_lim, sliding=200, debug=False):
    """Taking the best between different windows in pretrigger. Same variables than "compute_pedestal_variables_sliding_window". It checks for the best window.
    
    :param ADC: array containing the ADCs.
    :type ADC: nparray
    :param ped_lim: size in bins of the sliding window.
    :type ped_lim: int
    :param sliding: bins moved between shifts of the window, defaults to 200
    :type sliding: int, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: ADC_s, start_window -- shifted ADCs and start window.
    :rtype: nparray, nparray
    """
    if ped_lim < sliding:
        ped_lim = sliding
        rprint(
            "[yellow]WARNING: Pedestal window is smaller than sliding window. Setting ped_lim = %s[/yellow]"
            % sliding
        )

    slides = int(ped_lim / sliding)
    nwvfs = ADC.shape[0]
    aux = np.zeros((nwvfs, slides))

    for i in range(slides):
        aux[:, i] = np.std(ADC[:, (i * sliding) : ((i + 1) * sliding)], axis=1)
    try:
        start_window = np.argmin(aux, axis=1) * sliding
    except ValueError:
        rprint("[red]ERROR: There is a problem with the pedestal computation. Check the data![/red]")
        start_window = np.zeros(nwvfs)

    ADC_s = shift_ADCs(ADC, (-1) * start_window)

    if debug:
        rprint(
            "[cyan]Calculating pedestal variables from sliding window of %i bins[/cyan]" % (sliding)
        )
    return ADC_s, start_window


def compute_power_spec(ADC, timebin, debug=False):
    """Computes the power spectrum of the given events. It returns both axis.
    
    :param ADC: array containing the ADCs.
    :type ADC: nparray
    :param timebin: timebin of the data.
    :type timebin: float
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: power spectrum and frequency axis.
    :rtype: nparray, nparray
    """

    aux = []
    aux_X = np.fft.rfftfreq(len(ADC[0]), timebin)
    for i in range(len(ADC)):
        aux.append(np.fft.rfft(ADC[i]))

    return np.absolute(np.mean(aux, axis=0)), np.absolute(aux_X)


@numba.njit
def shift_ADCs(ADC, shift, debug=False):
    """Used for the sliding window.
    
    :param ADC: array containing the ADCs.
    :type ADC: nparray
    :param shift: array containing the shift values.
    :type shift: nparray
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: aux_ADC -- shifted ADCs.
    :rtype: nparray
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
    """Used for the sliding window.
    
    :param arr: array containing the ADCs.
    :type arr: nparray
    :param num: array containing the shift values.
    :type num: nparray
    :param fill_value: value to be inserted in the empty bins, defaults to 0
    :type fill_value: int, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: arr -- shifted array.
    :rtype: nparray
    """

    if num > 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    elif num < 0:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    else:
        return arr


# ===========================================================================#
# ********************** AVERAGING FUCNTIONS ********************************#
# ===========================================================================#


def average_wvfs(
    my_runs,
    info,
    key,
    label,
    centering="NONE",
    threshold=0,
    cut_label="",
    OPT={},
    debug=False,
):
    """This function calculates the average waveform of a run. 
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param centering: centering method (NONE, PEAK, THRESHOLD), defaults to "NONE"
    :type centering: str, optional
    :param threshold: threshold value, defaults to 0
    :type threshold: int, optional
    :param cut_label: label for the cut, defaults to ""
    :type cut_label: str, optional
    :param OPT: dictionary containing the options, defaults to {}
    :type OPT: dict, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    """

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            generate_cut_array(my_runs)
        if check_key(my_runs[run][ch], "UnitsDict") == False:
            get_run_units(my_runs)

        buffer = 200
        aux_ADC = my_runs[run][ch][key][my_runs[run][ch]["MyCuts"] == True]

        values, counts = np.unique(
            np.argmax(aux_ADC, axis=1), return_counts=True
        )  # using the mode peak as reference
        bin_ref_peak = values[np.argmax(counts)]
        if bin_ref_peak < buffer:
            bin_ref_peak = buffer

        # AveWvf: each event is added without centering.
        if centering == "NONE": 
            my_runs[run][ch][label + "AveWvf" + cut_label] = np.asarray(
                [np.mean(aux_ADC, axis=0)]
            )  # It saves the average waveform as "AveWvf_*"
        
        # AveWvfPeak: each event is centered according to wvf argmax.
        if centering == "PEAK":
            bin_max_peak = np.argmax(
                aux_ADC[:, bin_ref_peak - buffer : bin_ref_peak + buffer], axis=1
            )
            bin_max_peak = bin_max_peak + bin_ref_peak - buffer
            for ii in range(len(aux_ADC)):
                aux_ADC[ii] = np.roll(
                    aux_ADC[ii], bin_ref_peak - bin_max_peak[ii]
                )  # It centers the waveform using the peak
            my_runs[run][ch][label + "AveWvfPeak" + cut_label] = np.asarray(
                [np.mean(aux_ADC, axis=0)]
            )  # It saves the average waveform as "AveWvfPeak_*"
        
        # AveWvfThreshold: each event is centered according to first wvf entry exceding a threshold.
        if centering == "THRESHOLD":
            if threshold == 0:
                threshold = np.max(np.mean(aux_ADC, axis=0)) / 2
            values, counts = np.unique(
                np.argmax(aux_ADC > threshold, axis=1), return_counts=True
            )  # using the mode peak as reference
            bin_ref_thld = values[np.argmax(counts)]  # It is an int
            bin_max_thld = np.argmax(
                aux_ADC[:, bin_ref_peak - buffer : bin_ref_peak + buffer] > threshold,
                axis=1,
            )
            bin_max_thld = bin_max_thld + bin_ref_thld - buffer
            for ii in range(len(aux_ADC)):
                aux_ADC[ii] = np.roll(
                    aux_ADC[ii], bin_ref_thld - bin_max_thld[ii]
                )  # It centers the waveform using the threshold
            my_runs[run][ch][label + "AveWvfThreshold" + cut_label] = np.asarray(
                [np.mean(aux_ADC, axis=0)]
            )  # It saves the average waveform as "AveWvfThreshold_*"

    rprint(
        "[green]--> Computed Average Wvfs (centered wrt %s)!!![/green]" % centering
    )


def expo_average(my_run, alpha, debug=False):
    """This function calculates the exponential average with a given alpha.
    
    :param my_run: run we want to use.
    :type my_run: nparray
    :param alpha: alpha value.
    :type alpha: float
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: v_averaged -- averaged run computed as average[i+1] = (1-alpha) * average[i] + alpha * my_run[i+1]
    :rtype: nparray
    """
 
    v_averaged = np.zeros(len(my_run))
    v_averaged[0] = my_run[0]
    for i in range(len(my_run) - 1):
        v_averaged[i + 1] = (1 - alpha) * v_averaged[i] + alpha * my_run[
            i + 1
        ]  # e.g. alpha = 0.1  ->  average[1] = 0.9 * average[0] + 0.1 * my_run[1]

    return v_averaged


def unweighted_average(my_run, debug=False):
    """This function calculates the unweighted average.
    
    :param my_run: run we want to use.
    :type my_run: nparray
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: v_averaged -- averaged run computed as average[i+1] = (my_run[i] + my_run[i+1] + my_run[i+2]) / 3
    :rtype: nparray
    """

    v_averaged = np.zeros(len(my_run))
    v_averaged[0] = my_run[0]
    v_averaged[-1] = my_run[-1]

    for i in range(len(my_run) - 2):
        v_averaged[i + 1] = (
            my_run[i] + my_run[i + 1] + my_run[i + 2]
        ) / 3  # e.g. average[1] = (my_run[0] + my_run[1] + my_run[2]) / 3

    return v_averaged


def smooth(my_run, alpha, debug=False):
    """This function calculates the exponential average and then the unweighted average.
    
    :param my_run: run we want to use.
    :type my_run: nparray
    :param alpha: alpha value.
    :type alpha: float
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: my_run -- averaged run computed as average[i+1] = (my_run[i] + my_run[i+1] + my_run[i+2]) / 3 with my_run = (1-alpha) * average[i] + alpha * my_run[i+1]
    :rtype: nparray
    """

    my_run = expo_average(my_run, alpha)
    my_run = unweighted_average(my_run)
    return my_run


# ===========================================================================#
# ********************** INTEGRATION FUNCTIONS ******************************#
# ===========================================================================#


def find_baseline_cuts(raw, debug=False):
    """It finds the cuts with the x-axis. It returns the index of both bins.
    
    :param raw: the np array that you want to analize.
    :type raw: nparray
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: i_idx, f_idx -- initial and final index of the cuts.
    :rtype: int, int
    """

    max = np.argmax(raw)
    i_idx = 0
    f_idx = 0
    for j in range(len(raw[max:])):  # Before the peak
        if raw[max + j] < 0:
            f_idx = max + j
            break  # Looks for the change of sign
    for j in range(len(raw[:max])):  # After the peak
        if raw[max - j] < 0:
            i_idx = max - j + 1
            break  # Looks for the change of sign

    return i_idx, f_idx


def find_amp_decrease(raw, thrld, debug=False):
    """It finds bin where the amp has fallen above a certain threshold relative to the main peak. It returns the index of both bins.
    
    :param raw: the np array that you want to analize.
    :type raw: nparray
    :param thrld: the relative amp that you want to analize.
    :type thrld: float
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: i_idx, f_idx -- initial and final index of the cuts.
    :rtype: int, int
    """

    max = np.argmax(raw)
    i_idx = 0
    f_idx = 0
    for j in range(len(raw[max:])):  # Before the peak
        if raw[max + j] < np.max(raw) * thrld:
            f_idx = max + j
            break  # Looks for the change of sign (including thrld)
    for j in range(len(raw[:max])):  # After the peak
        if raw[max - j] < np.max(raw) * thrld:
            i_idx = max - j + 1
            break  # Looks for the change of sign (including thrld)

    return i_idx, f_idx


def integrate_wvfs(my_runs, info, key, label, cut_label="", debug=False):
    """This function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted (by default any ADC).
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param cut_label: label for the cut, defaults to ""
    :type cut_label: str, optional
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return my_runs: dictionary containing the data with the integrated values.
    :rtype: dict
    """
    # If I_RANGE == -1 it fixes t0 to pedestal time and it integrates the time indicated in F_RANGE, e.g. I_RANGE = -1 F_RANGE = 6e-6 it integrates 6 microsecs from pedestal time.
    # If I_RANGE != -1 it integrates from the indicated time to the F_RANGE value, e.g. I_RANGE = 2.1e-6 F_RANGE = 4.3e-6 it integrates in that range.
    # I_RANGE must have same length than F_RANGE!

    integration_dict = {"ChargeAveRange": {}, "ChargePedRange": {}, "ChargeRange": {}}
    conversion_factor = (
        info["DYNAMIC_RANGE"][0] / info["BITS"][0]
    )  # Amplification factor of the system
    ch_amp = dict(
        zip(info["CHAN_TOTAL"], info["CHAN_AMPLI"])
    )  # Creates a dictionary with amplification factors according to each detector

    i_range = info["I_RANGE"]  # Get initial time(s) to start the integration
    f_range = info["F_RANGE"]  # Get final time(s) to finish the integration

    if debug:
        rprint(
            "[magenta]\n--- Integrating RUN %s CH %s TYPE %s, REF %s ---[/magenta]"
            % (my_runs["NRun"], my_runs["NChannel"], info["TYPE"], info["REF"])
        )
    for run, ch, typ, ref in product(
        my_runs["NRun"], my_runs["NChannel"], info["TYPE"], info["REF"]
    ):
        if check_key(my_runs[run][ch], "MyCuts") == False:
            generate_cut_array(my_runs)
        if check_key(my_runs[run][ch], "UnitsDict") == False:
            get_run_units(my_runs)  # If there are no units, it calculates them
        if check_key(my_runs[run][ch], label + "ChargeRangeDict") == False:
            my_runs[run][ch][
                label + "ChargeRangeDict"
            ] = {}  # Creates a dictionary with ranges for each ChargeRange entry

        ave = my_runs[run][ch][
            label + ref + cut_label
        ]  # Load the reference average waveform
        aux_ADC = my_runs[run][ch][key]
        for i in range(len(ave)):
            if typ == "ChargeAveRange":  # Integrated charge from the average waveform
                i_idx, f_idx = find_baseline_cuts(ave[i])
                if f_idx - i_idx <= 0:
                    rprint(
                        "[yellow]WARNING: Invalid integration range for RUN %s CH %s TYPE %s, REF %s[/yellow]"
                        % (run, ch, typ, label + ref)
                    )
                    idx, f_idx = find_amp_decrease(ave[i], 1e-3)
                    if debug:
                        rprint(
                            "[magenta]Using amp decrease instead: [%.2f, %.2f] \u03BCs[/magenta]"
                            % (
                                idx * my_runs[run][ch]["Sampling"],
                                f_idx * my_runs[run][ch]["Sampling"],
                            )
                        )
                charge_name = label + typ + ref.split("Wvf")[-1] + cut_label
                my_runs[run][ch][charge_name] = np.sum(
                    aux_ADC[:, i_idx:f_idx], axis=1
                )  # Integrated charge from the DECONVOLUTED average waveform
                rprint(
                    "[green]--> Computed %s (according to type **%s** from %.2E to %.2E)!!![/green]"
                    % (
                        charge_name,
                        typ,
                        i_idx * my_runs[run][ch]["Sampling"],
                        f_idx * my_runs[run][ch]["Sampling"],
                    )
                )
                integration_dict[typ][charge_name] = [int(i_idx), int(f_idx)]

        if typ == "ChargePedRange":
            for j in range(len(f_range)):
                i_idx = my_runs[run][ch][label + "PedLim"]
                f_idx = i_idx + int(
                    np.round(f_range[j] * 1e-6 / my_runs[run][ch]["Sampling"])
                )
                charge_name = label + typ + str(j) + cut_label
                my_runs[run][ch][charge_name] = np.sum(aux_ADC[:, i_idx:f_idx], axis=1)
                rprint(
                    "[green]--> Computed %s (according to type **%s** from %.2E to %.2E)!!![/green]"
                    % (
                        charge_name,
                        typ,
                        i_idx * my_runs[run][ch]["Sampling"],
                        f_idx * my_runs[run][ch]["Sampling"],
                    )
                )
                integration_dict[typ][charge_name] = [int(i_idx), int(f_idx)]

        if typ == "ChargeRange":
            for k in range(len(f_range)):
                i_idx = int(np.round(i_range[k] * 1e-6 / my_runs[run][ch]["Sampling"]))
                f_idx = int(np.round(f_range[k] * 1e-6 / my_runs[run][ch]["Sampling"]))
                this_aux_ADC = shift_ADCs(
                    aux_ADC,
                    -np.asarray(my_runs[run][ch][label + "PeakTime"]) + i_idx,
                    debug=debug,
                )
                charge_name = label + typ + str(k) + cut_label
                my_runs[run][ch][charge_name] = np.sum(this_aux_ADC[:, :f_idx], axis=1)
                rprint(
                    "[green]--> Computed %s (according to type **%s** from %.2E to %.2E)!!![/green]"
                    % (
                        charge_name,
                        typ,
                        i_idx * my_runs[run][ch]["Sampling"],
                        f_idx * my_runs[run][ch]["Sampling"],
                    )
                )
                integration_dict[typ][charge_name] = [int(i_idx), int(f_idx)]

    # rprintintegration_dict)
    out_path = info["NPY_PATH"][0]
    out_path = os.path.expandvars(out_path)

    filename = f'{root}/{info["NPY_PATH"][0]}/run{run.zfill(2)}_ch{ch}/ChargeDict.yml'
    update_yaml_file(filename, integration_dict, convert=False, debug=debug)
    
    return my_runs


def compute_peak_RMS(my_runs, info, key, label, debug=False):
    """This function uses the calculated average wvf for a given run and computes the RMS of the peak in the given buffer.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param info: dictionary containing the info.
    :type info: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return my_runs: dictionary containing the data with the RMS values.
    :rtype: dict
    """
    
    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        ref = np.asarray(my_runs[run][ch][label + "AveWvf"][0])
        i_idx, f_idx = find_baseline_cuts(ref)
        if f_idx - i_idx <= 0:
            rprint(
                "[yellow]WARNING: Invalid integration range for RUN %s CH %s, REF %s[/yellow]"
                % (run, ch, label + "AveWvf")
            )
            idx, f_idx = find_amp_decrease(ref, 1e-3)
            if debug:
                rprint(
                    "[magenta]Using amp decrease instead: [%.2E, %.2E] \u03BCs[/magenta]"
                    % (
                        idx * my_runs[run][ch]["Sampling"],
                        f_idx * my_runs[run][ch]["Sampling"],
                    )
                )
            if f_idx - i_idx <= 0:
                rprint(
                    "[red]ERROR: Invalid integration range for RUN %s CH %s, REF %s[/red]"
                    % (run, ch, label + "AveWvf"))
                idx, f_idx = (
                    my_runs[run][ch][label + "PedLim"],
                    my_runs[run][ch][label + "PedLim"] + 1000,
                )
                if debug:
                    rprint(
                        "[magenta]Using pedlim instead: [%.2E, %.2E] \u03BCs[/magenta]"
                        % (
                            idx * my_runs[run][ch]["Sampling"],
                            f_idx * my_runs[run][ch]["Sampling"],
                        )
                    )

        pulse_peak = np.argmax(ref)
        pulse_max = np.max(ref)
        pulse_width = f_idx - i_idx

        shift_idx = my_runs[run][ch][label + "PeakTime"] - (pulse_peak - i_idx)
        shift_idx[shift_idx < 0] = 0
        aux_ADC = shift_ADCs(my_runs[run][ch][key], -shift_idx, debug=debug)
        aux_ADC = np.asarray(aux_ADC)
        my_runs[run][ch][label + "RMS"] = np.sqrt(
            np.mean(
                np.power(
                    aux_ADC[:, :pulse_width].T
                    - np.tile(ref[i_idx:f_idx], (len(aux_ADC), 1)).T
                    * np.max(aux_ADC[:, :pulse_width], axis=1)
                    / pulse_max,
                    2,
                ),
                axis=0,
            )
        )
        rprint("[green]--> Computed Peak RMS!!![/green]")


# ===========================================================================#
# ************************ GENERAL FUNCTIONS ********************************#
# ===========================================================================#


def insert_variable(my_runs, var, key, debug=False):
    """Insert values for each type of signal.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param var: array of values to be inserted.
    :type var: nparray
    :param key: key to be inserted.
    :type key: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
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
                rprint("[magenta]Inserting value...[/magenta]")


def get_ADC_key(my_runs, key, debug=False):
    """This function returns the ADC key for a given run.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param key: key to be inserted.
    :type key: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: key, label -- key and label for the ADC.
    :rtype: str, str
    """

    found_duplicate = 0
    if key == "":
        for this_key in my_runs[my_runs["NRun"][0]][my_runs["NChannel"][0]].keys():
            if "ADC" in this_key:
                key = this_key
                label = this_key.split("ADC")[0]
                found_duplicate += 1
                if debug:
                    rprint("[magenta]Found ADC branch: %s[/magenta]" % key)
                if found_duplicate > 1:
                    rprint(
                        "[red]ERROR: Found more than one ADC key! Please check load preset.[/red]"
                    )
                    exit()
        if found_duplicate == 0:
            rprint("[yellow]WARNING: No ADC branch found![/yellow]")
            label = ""
        if debug:
            rprint(
                "[green]--> Returning key: '%s' and label: '%s'!!![/green]" % (key, label)
            )

    else:
        label = key.split("ADC")[0]
        if debug:
            rprint("[magenta]Returning label from provided key[/magenta]")

    return key, label


def get_wvf_label(my_runs, key, label, debug=False):
    """This function returns the label for a given run. This depends on the found ADC key or the one provided by the user.
    
    :param my_runs: dictionary containing the data.
    :type my_runs: dict
    :param key: key to be inserted.
    :type key: str
    :param label: label to be inserted.
    :type label: str
    :param debug: boolean to print debug messages, defaults to False
    :type debug: bool, optional
    
    :return: out_key, out_label -- key and label for the ADC.
    :rtype: str, str
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
                rprint(
                    "[yellow]WARNING: Provided label does not match found label![/yellow]"
                )
            user_confirmation = input(
                "Do you want to continue with coustom selection? [y/n]: "
            )
            if user_confirmation.lower() in ["y", "yes"]:
                out_label = found_label
                if debug:
                    rprint("[magenta]Selected label %s[/magenta]" % label)
            else:
                out_label = label
                if debug:
                    rprint("[magenta]Found label %s[/magenta]" % found_label)
        else:
            out_label = found_label
            if debug:
                rprint("[magenta]Found label %s[/magenta]" % label)

    elif key != "" and label == "":
        if debug:
            rprint(
                "[yellow]WARNING: Selected input ADC but no label provided![/yellow]"
            )
        found_key, found_label = get_ADC_key(my_runs, key, debug=debug)
        out_key = found_key
        out_label = found_label
        if found_label != key.split("ADC")[0]:
            rprint(
                "[red]ERROR: Found label does not match label from provided key![/red]"
            )
            exit()

    else:
        if debug:
            rprint(
                "[yellow]WARNING: Using full coustom mode for label and ADC key selection![/yellow]"
            )
        out_key = key
        out_label = label

    return out_key, out_label
