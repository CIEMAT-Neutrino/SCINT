import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from rich import print as rprint

# Imports from other libraries
from srcs.utils import get_project_root
from ..io_functions import check_key
from ..head_functions import update_yaml_file
from ..ana_functions import (
    generate_cut_array,
    get_run_units,
    get_wvf_label,
    shift_ADCs,
    compute_ana_wvfs,
)

root = get_project_root()

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
    """
    \nIt calculates the average waveform of a run. Select centering:
    \n- "NONE"      -> AveWvf: each event is added without centering.
    \n- "PEAK"      -> AveWvfPeak: each event is centered according to wvf argmax.
    \n- "THRESHOLD" -> AveWvfThreshold: each event is centered according to first wvf entry exceding a threshold.
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

        if centering == "NONE":
            my_runs[run][ch][label + "AveWvf" + cut_label] = np.asarray(
                [np.mean(aux_ADC, axis=0)]
            )  # It saves the average waveform as "AveWvf_*"

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
    """
    \nThis function calculates the exponential average with a given alpha.
    \n**returns**: average[i+1] = (1-alpha) * average[i] + alpha * my_run[i+1]
    """
    v_averaged = np.zeros(len(my_run))
    v_averaged[0] = my_run[0]
    for i in range(len(my_run) - 1):
        v_averaged[i + 1] = (1 - alpha) * v_averaged[i] + alpha * my_run[
            i + 1
        ]  # e.g. alpha = 0.1  ->  average[1] = 0.9 * average[0] + 0.1 * my_run[1]

    return v_averaged


def unweighted_average(my_run, debug=False):
    """
    \nThis function calculates the unweighted average.
    \n**returns**: average[i+1] = (my_run[i] + my_run[i+1] + my_run[i+2]) / 3
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
    """
    \nThis function calculates the exponential average and then the unweighted average.
    \n**returns**: average[i+1] = (my_run[i] + my_run[i+1] + my_run[i+2]) / 3 with my_run = (1-alpha) * average[i] + alpha * my_run[i+1]
    """
    my_run = expo_average(my_run, alpha)
    my_run = unweighted_average(my_run)
    return my_run


# ===========================================================================#
# ********************** INTEGRATION FUNCTIONS ******************************#
# ===========================================================================#


def find_baseline_cuts(raw, debug=False):
    """
    \nIt finds the cuts with the x-axis. It returns the index of both bins.
    \n**VARIABLES:**
    \n- raw: the .root that you want to analize.
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
    """
    \nIt finds bin where the amp has fallen above a certain threshold relative to the main peak. It returns the index of both bins.
    \n**VARIABLES:**
    \n- raw: the np array that you want to analize.
    \n- thrld: the relative amp that you want to analize.
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
    """
    \nThis function integrates each event waveform. There are several ways to do it and we choose it with the argument "types".
    \n**VARIABLES**:
    \n- my_runs: run(s) we want to use
    \n- info: input information from .txt with DAQ characteristics and Charge Information.
    \n- key: waveform we want to integrate (by default any ADC)
    \nIn txt Charge Info part we can indicate the type of integration, the reference average waveform and the ranges we want to integrate.
    \nIf I_RANGE == -1 it fixes t0 to pedestal time and it integrates the time indicated in F_RANGE, e.g. I_RANGE = -1 F_RANGE = 6e-6 it integrates 6 microsecs from pedestal time.
    \nIf I_RANGE != -1 it integrates from the indicated time to the F_RANGE value, e.g. I_RANGE = 2.1e-6 F_RANGE = 4.3e-6 it integrates in that range.
    \nI_RANGE must have same length than F_RANGE!
    """

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
            "\n--- Integrating RUN %s CH %s TYPE %s, REF %s ---"
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
                            "Using amp decrease instead: [%.2f, %.2f] \u03BCs"
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

    # rprint(integration_dict)
    out_path = info["NPY_PATH"][0]
    out_path = os.path.expandvars(out_path)

    filename = f'{root}/{info["NPY_PATH"][0]}/run{run.zfill(2)}/ch{ch}/ChargeDict.yml'
    update_yaml_file(filename, integration_dict, convert=False, debug=debug)
    return my_runs


def compute_peak_RMS(my_runs, info, key, label, debug=False):
    """
    \nThis function uses the calculated average wvf for a given run and computes the RMS of the peak in the given buffer.
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
                    "Using amp decrease instead: [%.2E, %.2E] \u03BCs"
                    % (
                        idx * my_runs[run][ch]["Sampling"],
                        f_idx * my_runs[run][ch]["Sampling"],
                    )
                )
            if f_idx - i_idx <= 0:
                rprint(
                    "[red]ERROR: Invalid integration range for RUN %s CH %s, REF %s[/red]"
                    % (run, ch, label + "AveWvf"),
                )
                idx, f_idx = (
                    my_runs[run][ch][label + "PedLim"],
                    my_runs[run][ch][label + "PedLim"] + 1000,
                )
                if debug:
                    rprint(
                        "Using pedlim instead: [%.2E, %.2E] \u03BCs"
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
