# ================================================================================================================================================#
# In this library we have all the functions related with visualization. They are mostly used in 0XVis*.py macros but can be included anywhere !! #
# ================================================================================================================================================#
from srcs.utils import get_project_root

import math, inquirer, scipy, yaml, os, stat
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import pandas as pd

# Imports from other libraries
from typing import Optional
from itertools import product
from rich import print as rprint
from matplotlib.cm import viridis
from scipy.signal import find_peaks
from matplotlib.colors import LogNorm
from scipy.ndimage.interpolation import shift
from scipy.signal import savgol_filter

# Imports from this library
from .io_functions import check_key, save_figure
from .fig_config import figure_features, add_grid
from .unit_functions import get_run_units
from .sty_functions import style_selector, get_prism_colors

root = get_project_root()


def vis_npy(my_run, info, keys, OPT={}, save=False, debug=False):
    """This function is a event visualizer. It plots individual events of a run, indicating the pedestal level, pedestal std and the pedestal calc limit. We can interact with the plot and pass through the events freely (go back, jump to a specific event...)
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param info: info dictionary
    :type info: dict
    :param keys: choose between ADC or AnaADC to see raw (as get from ADC) or Analyzed events (starting in 0 counts), respectively
    :type keys: list
    :param OPT: several options that can be True or False
        (a) MICRO_SEC: if True we multiply Sampling by 1e6
        (b) NORM: True if we want normalized waveforms
        (c) LOGY: True if we want logarithmic y-axis
        (d) SHOW_AVE: if computed and True, it will show average
        (e) SHOW_PARAM: True if we want to check calculated parameters (pedestal, amplitude, charge...)
        (f) CHARGE_KEY: if computed and True, it will show the parametre value
        (g) PEAK_FINDER: True if we want to check how many peaks are
        (h) CUTTED_WVF: choose the events we want to see. If -1 all events are displayed, if 0 only uncutted events are displayed, if 1 only cutted events are displayed
        (i) SAME_PLOT: True if we want to plot different channels in the SAME plot
    :type OPT: dict
    :param save: True if we want to save the plot
    :type save: bool
    :param debug: True if we want to print debug messages
    :type debug: bool
    
    :return: None
    """

    colors = get_prism_colors()
    if not check_key(OPT, "CUTTED_WVF"):
        OPT["CUTTED_WVF"] = -1
        rprint("[yellow]CUTTED_WVF not defined, setting to -1[/yellow]")
    if not check_key(OPT, "SAME_PLOT"):
        OPT["SAME_PLOT"] = False
        rprint("[yellow]SAME_PLOT not defined, setting to False[/yellow]")

    axs = []
    style_selector(OPT)
    ch_list = my_run["NChannel"]
    nch = len(my_run["NChannel"])

    for run, key in product(my_run["NRun"], keys):
        plt.ion()
        if OPT["SAME_PLOT"] == False:
            if nch < 4:
                # fig, ax = plt.subplots(nch, 1, figsize=(10, 8))
                fig, ax = plt.subplots(nch, 1)
                if nch == 1:
                    axs.append(ax)
                else:
                    axs = ax
            else:
                # fig, ax = plt.subplots(2, math.ceil(nch / 2), figsize=(10, 8))
                fig, ax = plt.subplots(2, math.ceil(nch / 2))
                axs = ax.T.flatten()
        else:
            # fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            fig, ax = plt.subplots(1, 1)
            axs = ax

        idx = 0
        if check_key(my_run[run][ch_list[0]], "MyCuts") == False:
            # generate_cut_array(my_run, debug=debug)
            if "RawADC" not in my_run[run][ch_list[0]]:
                rprint("[red]RawADC not found![/red]")
                ref_variable = "AnaADC"
            elif "AnaADC" not in my_run[run][ch_list[0]]:
                rprint("[red]RawADC is empty![/red]")
                ref_variable = "RawADC"
            my_run[run][ch_list[0]]["MyCuts"] = np.zeros(
                len(my_run[run][ch_list[0]][ref_variable]), dtype=bool
            )
        
        while idx < len(my_run[run][ch_list[0]]["MyCuts"]):
            try:
                skip = 0
                for ch in ch_list:
                    if (
                        OPT["CUTTED_WVF"] == 0
                        and my_run[run][ch]["MyCuts"][idx] == False
                    ):
                        skip = 1
                        break  # To Skip Cutted events!!
                    if (
                        OPT["CUTTED_WVF"] == 1
                        and my_run[run][ch]["MyCuts"][idx] == True
                    ):
                        skip = 1
                        break  # To Get only Cutted events!!
                if skip == 1:
                    idx = idx + 1
                    continue
            except:
                pass

            fig.supxlabel(r"Time [s]")
            fig.supylabel("ADC Counts")
            raw = []
            filtered_ana = []
            norm_raw = [
                1
            ] * nch  # Generates a list with the norm correction for std bar

            for j in range(nch):
                if key == "AnaADC":
                    rprint(
                        "[yellow]\nAnaADC not saved but we compute it now :)[/yellow]"
                    )
                    label = "Ana"
                    ana = my_run[run][ch_list[j]]["PChannel"] * (
                        (
                            my_run[run][ch_list[j]]["RawADC"][idx].T
                            - my_run[run][ch_list[j]]["Raw" + info["PED_KEY"][0]][idx]
                        ).T
                    )
                    # if "WVF_FILTER" in OPT and OPT["WVF_FILTER"]:
                    #     rprint("[cyan]Filtering waveforms![/cyan]")
                    #     filtered_ana.append(filter_wvf(ana))
                    raw.append(ana)
                    ped = 0
                    std = my_run[run][ch_list[j]]["AnaPedSTD"][idx]
                    if debug:
                        rprint("[magenta]Using '%s' label[/magenta]" % label)

                else:
                    label = key.split("ADC")[0]
                    raw.append(my_run[run][ch_list[j]][key][idx])
                    ped = my_run[run][ch_list[j]][label + info["PED_KEY"][0]][idx]
                    std = my_run[run][ch_list[j]][label + "PedSTD"][idx]
                    if debug:
                        rprint("[magenta]Using '%s' label[/magenta]" % label)

                if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
                    norm_raw[j] = np.max(raw[j])
                    raw[j] = raw[j] / np.max(raw[j])

                sampling = my_run[run][ch_list[j]][
                    "Sampling"
                ]  # To reset the sampling to its initial value (could be improved)
                if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"] == True:
                    fig.supxlabel(r"Time [$\mu$s]")
                    my_run[run][ch_list[j]]["Sampling"] = (
                        my_run[run][ch_list[j]]["Sampling"] * 1e6
                    )

                # if OPT["SAME_PLOT"] == False:
                if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                    axs[j].semilogy()
                    std = 0  # It is ugly if we see this line in log plots
                # fig.tight_layout(h_pad=2) # If we want more space betweeb subplots. We avoid small vertical space between plots
                axs[j].plot(
                    my_run[run][ch_list[j]]["Sampling"] * np.arange(len(raw[j])),
                    raw[j],
                    label="%s" % key,
                    drawstyle="steps",
                    alpha=0.95,
                    linewidth=1,
                    c=colors[0],
                    zorder=0,
                )
                if "WVF_FILTER" in OPT and OPT["WVF_FILTER"]:
                    axs[j].plot(
                        my_run[run][ch_list[j]]["Sampling"]
                        * np.arange(len(filtered_ana[j])),
                        filtered_ana[j],
                        label="%s" % key,
                        drawstyle="steps",
                        alpha=0.95,
                        linewidth=1,
                        c="red",
                        zorder=0,
                    )
                
                try:
                    axs[j].scatter(
                        my_run[run][ch_list[j]]["Sampling"]
                        * (my_run[run][ch_list[j]][label + "PeakTime"][idx] - 0.5),
                        my_run[run][ch_list[j]][label + "PeakAmp"][idx],
                        label="Peak",
                        c=colors[1],
                        zorder=10,
                    )
                except KeyError:
                    rprint("[red]PeakAmp not computed![/red]")
                # try: axs[j].scatter(
                #     my_run[run][ch_list[j]]["Sampling"]
                #     *my_run[run][ch_list[j]][label + "ValleyTime"][idx],
                #     my_run[run][ch_list[j]][label + "ValleyAmp"][idx],
                #     label="Valley", 
                #     c=colors[3], 
                #     zorder=10)
                # except KeyError: rprint("[red]ValleyAmp not computed![/red]")
                # try:
                #     axs[j].plot(
                #         my_run[run][ch_list[j]]["Sampling"]
                #         * np.array(
                #             [
                #                 my_run[run][ch_list[j]][label + "PedLim"],
                #                 my_run[run][ch_list[j]][label + "PedLim"],
                #             ]
                #         ),
                #         np.array([ped + 4 * std, ped - 4 * std]) / norm_raw[j],
                #         label="Pedestal limit",
                #         lw=2,
                #         c=colors[6],
                #         zorder=3,
                #     )
                # except KeyError:
                #     rprint("[red]PedLim not computed![/red]")
                # try:
                #     for value in ["SignalStart", "SignalEnd"]:
                #         axs[j].plot(
                #             my_run[run][ch_list[j]]["Sampling"]
                #             * np.array(
                #                 [
                #                     my_run[run][ch_list[j]][label + value][idx],
                #                     my_run[run][ch_list[j]][label + value][idx],
                #                 ]
                #             ),
                #             np.array([ped + 4 * std, ped - 4 * std]) / norm_raw[j],
                #             label="Signal window",
                #             lw=1.5,
                #             c=colors[8],
                #             zorder=3,
                #         )
                # except KeyError:
                #     rprint("[red]SignalWindow not computed![/red]")
                try:
                    for value in ["PedStart", "PedEnd"]:
                        axs[j].plot(
                            my_run[run][ch_list[j]]["Sampling"]
                            * np.array(
                                [
                                    my_run[run][ch_list[j]][label + value][idx],
                                    my_run[run][ch_list[j]][label + value][idx],
                                ]
                            ),
                            np.array([ped + 4 * std, ped - 4 * std]) / norm_raw[j],
                            label=value,
                            lw=1.5,
                            c=colors[6],
                            zorder=3,
                        )
                except KeyError:
                    rprint("[red]PedWindow not computed![/red]")
                try:
                    out_path = info["NPY_PATH"][0]
                    out_path = os.path.expandvars(out_path)
                    int_info = yaml.load(
                        open(
                            out_path
                            + "/run"
                            + str(run).zfill(2)
                            + f"/ch{ch_list[j]}/ChargeDict.yml"
                        ),
                        Loader=yaml.FullLoader,
                    )
                    for charge in int_info[OPT["CHARGE_KEY"]]:
                        for i in range(2):
                            axs[j].plot(
                                my_run[run][ch_list[j]]["Sampling"]
                                * np.array(
                                    [
                                        int_info[OPT["CHARGE_KEY"]][charge][i],
                                        int_info[OPT["CHARGE_KEY"]][charge][i],
                                    ]
                                ),
                                np.array([ped + 4 * std, ped - 4 * std]) / norm_raw[j],
                                lw=1.5,
                                c=colors[3],
                                zorder=3,
                            )
                except FileNotFoundError:
                    rprint("[red]ChargeDict.yml not found![/red]")
                axs[j].axhline((ped) / norm_raw[j], c="k", alpha=0.5, zorder=2)
                axs[j].axhline(
                    (ped + std) / norm_raw[j], c="k", alpha=0.5, ls="--", zorder=2
                )
                axs[j].axhline(
                    (ped - std) / norm_raw[j], c="k", alpha=0.5, ls="--", zorder=2
                )
                axs[j].set_title(
                    "Run {} - Ch {} - Event Number {}".format(run, ch_list[j], idx),
                )
                axs[j].xaxis.offsetText.set_fontsize(
                    14
                )  # Smaller fontsize for scientific notation
                axs[j].grid(True, alpha=0.7)

                if check_key(OPT, "SHOW_AVE") == True:
                    try:
                        ave_key = label + OPT["SHOW_AVE"]
                        ave = my_run[run][ch_list[j]][ave_key][0]
                        if OPT["NORM"] == True and OPT["NORM"] == True:
                            ave = ave / np.max(ave)
                        if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
                            ref_max_idx = np.argmax(raw[j])
                            idx_move = np.argmax(ave)
                            ave = shift(ave, ref_max_idx - idx_move, cval=0)
                        axs[j].plot(
                            my_run[run][ch_list[j]]["Sampling"] * np.arange(len(ave)),
                            ave,
                            label="%s" % ave_key,
                            drawstyle="steps",
                            lw=1.5,
                            c=colors[5],
                            alpha=0.5,
                            zorder=1,
                        )
                    except KeyError:
                        rprint(
                            f"[red]{label+OPT['SHOW_AVE']} has not been averaged![/red]"
                        )

                if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
                    axs[j].legend(loc="upper right", fontsize=7)

                if check_key(OPT, "PEAK_FINDER") == True and OPT["PEAK_FINDER"]:
                    # These parameters must be modified according to the run...
                    if check_key(my_run[run][ch_list[j]], "AveWvfSPE") == False:
                        thresh = (
                            my_run[run][ch_list[j]]["PedMax"][idx]
                            + 0.5 * my_run[run][ch_list[j]]["PedMax"][idx]
                        )
                    else:
                        thresh = np.max(my_run[run][ch_list[j]]["AveWvfSPE"]) * 3 / 4

                    wdth = 4
                    prom = 0.01
                    dist = 30
                    axs[j].axhline(thresh, c="k", alpha=0.6, ls="dotted")
                    peak_idx, _ = find_peaks(
                        raw[j],
                        height=thresh,
                        width=wdth,
                        prominence=prom,
                        distance=dist,
                    )
                    for p in peak_idx:
                        axs[j].scatter(
                            my_run[run][ch_list[j]]["Sampling"] * p,
                            raw[j][p],
                            c=colors[7],
                            alpha=0.9,
                        )

                try:
                    if my_run[run][ch_list[j]]["MyCuts"][idx] == False:
                        figure_features(tex=False)
                        axs[j].text(
                            0.5,
                            0.5,
                            s="CUT",
                            fontsize=100,
                            horizontalalignment="center",
                            verticalalignment="center",
                            transform=axs[j].transAxes,
                            color="red",
                            fontweight="bold",
                            alpha=0.5,
                        )
                        # figure_features()
                except:
                    pass

                if check_key(OPT, "SHOW_PARAM") == True and OPT["SHOW_PARAM"]:
                    rprint(
                        "[white,bold]\nEvent Number {} from RUN_{} CH_{} ({})[/white,bold]".format(
                            idx, run, ch_list[j], my_run[run][ch_list[j]]["Label"]))
                    try:
                        rprint("- Sampling:\t{:.0E}".format(sampling))
                    except KeyError:
                        rprint("[red]Sampling not found![/red]")
                    try:
                        rprint(
                            "- TimeStamp:\t{:.2E}".format(
                                my_run[run][ch_list[j]]["TimeStamp"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]TimeStamp not found![/red]")
                    try:
                        rprint(
                            "- Polarity:\t{}".format(
                                my_run[run][ch_list[j]]["PChannel"]
                            )
                        )
                    except KeyError:
                        rprint("[red]Polarity not found![/red]")
                    rprint("\n--- PreTrigger ---")
                    try:
                        rprint(
                            "- PreTrigger mean:\t{:.2E}".format(
                                my_run[run][ch_list[j]][label + "PreTriggerMean"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]PreTrigger mean not found![/red]")
                    try:
                        rprint(
                            "- PreTrigger std:\t{:.4f}".format(
                                my_run[run][ch_list[j]][label + "PreTriggerSTD"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]PreTrigger std not found![/red]")
                    try:
                        rprint(
                            "- PreTrigger min/max:\t{:.4f}/{:.4f}".format(
                                my_run[run][ch_list[j]][label + "PreTriggerMin"][idx],
                                my_run[run][ch_list[j]][label + "PreTriggerMax"][idx],
                            )
                        )
                    except KeyError:
                        rprint("[red]PreTrigger min/max not found![/red]")
                    try:
                        rprint(
                            "- PreTrigger limit:\t{:.2E}".format(
                                my_run[run][ch_list[j]]["Sampling"]
                                * my_run[run][ch_list[j]][label + "PedLim"]
                            )
                        )
                    except KeyError:
                        rprint("[red]PreTrigger time limit not found![/red]")
                    rprint("\n--- Pedestal from SlidingWindow Algorithm ---")
                    try:
                        rprint(
                            "- S. Pedestal mean:\t{:.2f}".format(
                                my_run[run][ch_list[j]][label + "PedMean"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]Pedestal mean not found![/red]")
                    try:
                        rprint(
                            "- S. Pedestal std:\t{:.4f}".format(
                                my_run[run][ch_list[j]][label + "PedSTD"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]Pedestal std not found![/red]")
                    try:
                        rprint(
                            "- S. Pedestal min/max:\t{:.4f}/{:.4f}".format(
                                my_run[run][ch_list[j]][label + "PedMin"][idx],
                                my_run[run][ch_list[j]][label + "PedMax"][idx],
                            )
                        )
                    except KeyError:
                        rprint("[red]Pedestal min/max not found![/red]")
                    try:
                        rprint(
                            "- S. Window start:\t{:.3E}".format(
                                my_run[run][ch_list[j]]["Sampling"]
                                * my_run[run][ch_list[j]][label + "PedStart"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]window start not found![/red]")
                    try:
                        rprint(
                            "- S. Window stop:\t{:.3E}".format(
                                my_run[run][ch_list[j]]["Sampling"]
                                * my_run[run][ch_list[j]][label + "PedEnd"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]window end not found![/red]")
                    rprint("\n--- Peak Variables ---")
                    try:
                        rprint(
                            "- Max peak amplitude:\t{:.2f}".format(
                                my_run[run][ch_list[j]][label + "PeakAmp"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]Max peak amplitude not found![/red]")
                    try:
                        rprint(
                            "- Max peak time:\t{:.3E}".format(
                                my_run[run][ch_list[j]][label + "PeakTime"][idx]
                                * my_run[run][ch_list[j]]["Sampling"]
                            )
                        )
                    except KeyError:
                        rprint("[red]Max peak time not found![/red]")
                    rprint("\n--- Valley Variables ---")
                    try:
                        rprint(
                            "- Min valley amplitude:\t{:.3E}".format(
                                my_run[run][ch_list[j]][label + "ValleyAmp"][idx]
                            )
                        )
                    except KeyError:
                        rprint("[red]Min valley amplitude not found![/red]")
                    try:
                        rprint(
                            "- Min valley time:\t{:.2E}".format(
                                my_run[run][ch_list[j]][label + "ValleyTime"][idx]
                                * my_run[run][ch_list[j]]["Sampling"]
                            )
                        )
                    except KeyError:
                        rprint("[red]Min valley time not found![/red]")
                    
                    rprint("\n--- Charge Variables ---")
                    try:
                        rprint(f"- {label} {OPT['CHARGE_KEY']}: {my_run[run][ch_list[j]][label+OPT['CHARGE_KEY']][idx]:.2E}")
                    except:
                        rprint(
                            "[yellow]- Charge: %s has not been computed![/yellow]"
                            % (label + OPT["CHARGE_KEY"])
                        )
                    
                    try:
                        rprint(
                            "- Peak_idx:",
                            peak_idx * my_run[run][ch_list[j]]["Sampling"],
                        )
                    except:
                        if not check_key(OPT, "PEAK_FINDER"):
                            rprint("")
                
                my_run[run][ch_list[j]]["Sampling"] = sampling

            tecla = input(
                "\nPress q to quit, p to save plot, r to go back, n to choose event or any key to continue: "
            )

            if tecla == "e":
                # Export plot data
                rprint("[yellow]Exporting data to txt...[/yellow]")
                # Check if the output path exists, if not create it
                if not os.path.exists(f'{root}/{info["OUT_PATH"][0]}/analysis/data'):
                    os.makedirs(f'{root}/{info["OUT_PATH"][0]}/analysis/data', mode=0o770, exist_ok=True)
                for j in range(nch):
                    # Open a file to save the data
                    rprint(f"[yellow]Saving file to {root}/{info['OUT_PATH'][0]}/analysis/data/run{run}_ch{ch_list[j]}_event{idx}.txt[/yellow]")
                    with open(
                        f'{root}/{info["OUT_PATH"][0]}/analysis/data/run{run}_ch{ch_list[j]}_event{idx}.txt',
                        "w",
                    ) as f:
                        f.write(
                            "# Time [ns]\tRawADC\tAnaADC\n"
                        )
                        for i in range(len(raw[j])):
                            f.write(
                                "{:.6f}\t{:.6f}\t{:.6f}\n".format(
                                    1e9 * my_run[run][ch_list[j]]["Sampling"] * i,
                                    raw[j][i],
                                    filtered_ana[j][i] if key == "AnaADC" else 0,
                                )
                            )

            elif tecla == "q":
                break
            elif tecla == "n":
                ev_num = int(input("Enter event number: "))
                idx = ev_num
                if idx > len(my_run[run][ch_list[j]]["MyCuts"]):
                    idx = len(my_run[run][ch_list[j]]["MyCuts"]) - 1
                    rprint(
                        "[yellow,bold]\nBe careful! There are %i in total[/yellow,bold]" % idx
                    )
            elif tecla == "p":
                save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, ch, f'{key}_Event{idx}', debug=debug)
                idx = idx + 1
            elif tecla == "r":
                idx = idx - 1
            else:
                idx = idx + 1
            if idx == len(my_run[run][ch_list[j]]["MyCuts"]):
                break
            try:
                [axs[j].clear() for j in range(nch)]
            except:
                axs.clear()
        try:
            [axs[j].clear() for j in range(nch)]
        except:
            axs.clear()
        plt.close()


def vis_compare_wvf(my_run, info, keys, OPT={}, save=False, debug=False):
    """This function is a waveform visualizer. It plots the selected waveform with the key and allow comparisson between runs/channels.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param info: info dictionary
    :type info: dict
    :param keys: waveform to plot (AveWvf, AveWvdSPE, ...)
    :type keys: list
    :param OPT: several options that can be True or False
        (a) MICRO_SEC: if True we multiply Sampling by 1e6
        (b) NORM: True if we want normalized waveforms
        (c) LOGY: True if we want logarithmic y-axis
        (d) COMPARE: "RUNS" to get a plot for each channel and the selected runs, "CHANNELS" to get a plot for each run and the selected channels
        (e) STATS: True if we want to print statistics
    :type OPT: dict
    :param save: True if we want to save the plot
    :type save: bool
    :param debug: True if we want to print debug messages
    :type debug: bool
    
    :return: None
    """

    style_selector(OPT)
    r_list = my_run["NRun"]
    if type(r_list) != list:
        try:
            r_list = r_list.tolist()
        except:
            rprint("[cyan]Imported runs as list![/cyan]")
    ch_loaded = my_run["NChannel"]
    if type(ch_loaded) != list:
        try:
            ch_loaded = ch_loaded.tolist()
        except:
            rprint("[cyan]Imported channels as list![/cyan]")
    nch = len(my_run["NChannel"])
    axs = []

    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        q = [
            inquirer.Checkbox(
                "channels",
                message="Select channels to plot?",
                choices=ch_loaded,
                default=ch_loaded,
            )
        ]
        ch_list = inquirer.prompt(q)["channels"]
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False:
        ch_list = ch_loaded

    a_list = r_list
    b_list = ch_list

    if not check_key(OPT, "COMPARE"):
        OPT["COMPARE"] = "NONE"
        rprint("[yellow]No comparison selected. Default is NONE[/yellow]")
    if OPT["COMPARE"] == "RUNS":
        a_list = ch_list
        b_list = r_list
    if OPT["COMPARE"] == "CHANNELS":
        a_list = r_list
        b_list = ch_list
    if OPT["COMPARE"] == "NONE":
        a_list = r_list
        b_list = ch_list
    for a_idx, a in enumerate(a_list):
        if OPT["COMPARE"] == "RUNS":
            ch = a
        if OPT["COMPARE"] == "CHANNELS":
            run = a
        if OPT["COMPARE"] == "NONE":
            run = a
            ch = b_list
        plt.ion()
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        axs = ax
        fig.supxlabel(r"Time [s]")
        fig.supylabel("ADC Counts")

        ref_max_idx = None
        for b_idx, b in enumerate(b_list):
            idx = a_idx * len(b_list) + b_idx
            if OPT["COMPARE"] == "RUNS":
                run = b
            if OPT["COMPARE"] == "CHANNELS":
                ch = b
            if OPT["COMPARE"] == "NONE":
                run = a
            if OPT["COMPARE"] not in ["RUNS", "CHANNELS", "NONE"]:
                exit("COMPARE must be RUNS, CHANNELS or NONE")
            if isinstance(keys, list):
                for key in keys:
                    ref_max_idx = plot_compare_wvf(
                        my_run,
                        info,
                        run,
                        ch,
                        key,
                        fig,
                        axs,
                        idx,
                        OPT,
                        ref_max_idx,
                        stats=OPT["STATS"],
                    )
                    rprint(f"Plotting run {run} ch {ch} {key} with index {idx}")
            elif isinstance(keys, dict):
                ref_max_idx = plot_compare_wvf(
                    my_run,
                    info,
                    run,
                    ch,
                    keys[(run, ch)],
                    fig,
                    axs,
                    idx,
                    OPT,
                    ref_max_idx,
                    stats=OPT["STATS"],
                )
            else:
                rprint(type(keys))
                exit("Keys must be a list or a dictionary")

        tecla = input("\nPress p to save plot and any key to continue: ")
        if tecla == "p":
            # if not os.path.exists(
            #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/'
            # ):
            #     os.makedirs(f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/', mode=0o770, exist_ok=True)
            #         # os.chmod(f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/', 0o770)
            if isinstance(keys, dict):
                save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, ch, f'{"_".join(list(keys.values()))}', debug=debug)

                # fig.savefig(
                #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_{"_".join(list(keys.values()))}.png',
                #     dpi=500,
                # )
            if isinstance(keys, list):
                save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, ch, f'{"_".join(keys)}', debug=debug)
                # fig.savefig(
                #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_{"_".join(keys)}.png',
                #     dpi=500,
                # )
        else:
            pass
        try:
            [axs[ch].clear() for ch in range(nch)]
        except:
            axs.clear()
        plt.close()


def plot_compare_wvf(
    my_run, info, run, ch, key, fig, axs, idx, OPT, ref_max_idx=None, stats=False
):
    """This function plots the waveform of the selected key. It allows to compare between runs or channels.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param info: info dictionary
    :type info: dict
    :param run: run we want to check
    :type run: int
    :param ch: channel we want to check
    :type ch: int
    :param key: key we want to plot
    :type key: str
    :param fig: figure to plot
    :type fig: matplotlib.figure.Figure
    :param axs: axis to plot
    :type axs: matplotlib.axes._subplots.AxesSubplot
    :param idx: index to plot
    :type idx: int
    :param OPT: several options that can be True or False
        (a) MICRO_SEC: if True we multiply Sampling by 1e6
        (b) NORM: True if we want normalized waveforms
        (c) LOGY: True if we want logarithmic y-axis
        (d) STATS: True if we want to print statistics
    :type OPT: dict
    :param ref_max_idx: index to align the waveforms
    :type ref_max_idx: int
    :param stats: True if we want to print statistics
    :type stats: bool
    
    :return: ref_max_idx
    :rtype: int
    """
    
    if OPT["COMPARE"] == "NONE":
        label = "Run {} - Channel {} ({}) - {}".format(
            run, ch, my_run[run][ch]["Label"], key
        )
        title = "Average Waveform"
    if OPT["COMPARE"] == "RUNS":
        label = "Run {} - {}".format(run, key)
        title = "Average Waveform - Ch {}".format(ch)
    if OPT["COMPARE"] == "CHANNELS":
        label = "Channel {} ({}) - {}".format(ch, my_run[run][ch]["Label"], key)
        title = "Average Waveform - Run {}".format(run)
    ave = my_run[run][ch][key][0]
    # counter = counter + 1
    if stats:
        rate = print_stats_terminal(my_run, (run, ch, key), ave)

    norm_ave = np.max(ave)
    sampling = my_run[run][ch][
        "Sampling"
    ]  # To reset the sampling to its initial value (could be improved)
    if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
        ave = ave / norm_ave
        fig.supylabel("Norm")
    if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"] == True:
        fig.supxlabel(r"Time [$\mu$s]")
        sampling = my_run[run][ch]["Sampling"] * 1e6
    if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
        axs.semilogy()
    if check_key(OPT, "ALIGN") == True and OPT["ALIGN"] == True:
        ref_threshold = np.argmax(ave > np.max(ave) * 2 / 3)
        if ref_max_idx is None:
            ref_max_idx = ref_threshold
        ave = np.roll(ave, ref_max_idx - ref_threshold)
    if check_key(OPT, "SPACE_OUT") and OPT["SPACE_OUT"] != 0:
        # for each b in b_list, we want to plot the same waveform with a different offset in x
        ave = np.roll(ave, int(idx) * int(OPT["SPACE_OUT"]))
    
    ave_smooth = savgol_filter(ave, window_length=11, polyorder=3)
    
    colors = get_prism_colors() + get_prism_colors()
    
    axs.plot(
        sampling * np.arange(len(ave)),
        ave_smooth,
        alpha=0.95,
        linewidth=1.2,
        label=label.replace("#", " "),
        c=colors[int(ch)],
    )
    
    # Adding the integration time window on the plot 
    npy_path = info["NPY_PATH"][0]
    range_path = f"{root}/{npy_path}/run{run}/ch{ch}/ChargeDict.yml"
    
    if os.path.exists(range_path):
        range_file = os.path.join(range_path)
        with open(range_file, 'r', encoding='latin1') as stream:
            charge_dict = yaml.safe_load(stream)
        
        rprint(f"[green]Plotting integration time window for run {run} ch {ch} loaded from {range_file}[/green]")
        int_range = charge_dict["ChargeAveRange"]["AnaChargeAveRange"]
        int_start_range = sampling*int_range[0]
        int_end_range = sampling*int_range[1]
        
        axs.axvline(x=int_start_range, color=colors[int(ch)], linestyle='--', lw=1, label=f'Int window ch{ch} = [{int_start_range:.2f} - {int_end_range:.2f}] $\mu$s')
        axs.axvline(x=int_end_range, color=colors[int(ch)], linestyle='--', lw=1)

    # Adding the PeakAmp time window on the plot 
    run_str = f"{int(run):02d}"
    if run_str in info["CALIB_RUNS"] :
        ch_idx = info["CHAN_TOTAL"].index(str(ch))
        ch_label = info["CHAN_LABEL"][ch_idx]
        if ch_label.startswith("SiPM"):
            center_tick = info["SIPM_PULSE"][0]
            half_width = info["WINDOW_SIPM_PULSE"][0]
        else:
            center_tick = info["CELL_PULSE"][0]
            half_width = info["WINDOW_CELL_PULSE"][0]

        peak_start_range = (center_tick - half_width)*sampling
        peak_end_range = (center_tick + half_width)*sampling

    else :
        peak_start_range = 0
        peak_end_range = sampling*len(ave)
    
    # axs.axvline(x=peak_start_range, color="grey", linestyle='--', lw=1, label=f'Peak window ch{ch} = [{peak_start_range:.2f} - {peak_end_range:.2f}] $\mu$s')
    # axs.axvline(x=peak_end_range, color="grey", linestyle='--', lw=1)
    
    axs.grid(True, alpha=0.7)
    axs.set_title(title, size=14)
    axs.xaxis.offsetText.set_fontsize(14)  # Smaller fontsize for scientific notation
    if check_key(OPT, "LIMITS") and OPT["LIMITS"]:
        axs.set_xlim(OPT["XLIM"][0], OPT["XLIM"][1])
        axs.set_ylim(OPT["YLIM"][0], OPT["YLIM"][1])

    if check_key(OPT, "LEGEND") == True and OPT["LEGEND"]:
        axs.legend()
        
    return ref_max_idx


def vis_var_hist(
    my_run,
    info,
    key,
    percentile=[0.1, 99.9],
    OPT={"SHOW": True},
    select_range=False,
    save=False,
    debug=False,
):
    """This function takes the specified variables and makes histograms. The binning is fix to 600, so maybe it is not the appropriate. Outliers are taken into account with the percentile. It discards values below and above the indicated percetiles. It returns values of counts, bins and bars from the histogram to be used in other function. WARNING! Maybe the binning stuff should be studied in more detail.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param info: info dictionary
    :type info: dict
    :param key: variables we want to plot as histograms. Type: List
        (a) PeakAmp: histogram of max amplitudes of all events. The binning is 1 ADC. There are not outliers.
        (b) PeakTime: histogram of times of the max amplitude in events. The binning is the double of the sampling. There are not outliers.
        (c) Other variable: any other variable. Here we reject outliers.
    :type key: list
    :param percentile: percentile used for outliers removal
    :type percentile: list
    :param OPT: several options that can be True or False
        (a) DENSITY: True if we want density histograms
        (b) ACCURACY: binning of the histogram
        (c) TERMINAL_MODE: True if we want to select the channels in the terminal
        (d) COMPARE: "RUNS" to get a plot for each channel and the selected runs, "CHANNELS" to get a plot for each run and the selected channels
        (e) SHOW: True if we want to show the plot
        (f) SAVE: True if we want to save the plot
    :type OPT: dict
    :param select_range: True if we want to select the range of the histogram
    :type select_range: bool
    :param save: True if we want to save the plot
    :type save: bool
    :param debug: True if we want to print debug messages
    :type debug: bool
    
    :return: all_counts, all_bins    
    """
    
    style_selector(OPT)
    all_counts = []
    all_bins = []
    all_bars = []
    r_list = my_run["NRun"]
    ch_loaded = my_run["NChannel"]
    if type(ch_loaded) != list:
        try:
            ch_loaded = ch_loaded.tolist()
        except:
            rprint("[cyan]Imported channels as list![/cyan]")

    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        q = [
            inquirer.Checkbox(
                "channels",
                message="Select channels to plot?",
                choices=ch_loaded,
                default=ch_loaded,
            )
        ]
        ch_list = inquirer.prompt(q)["channels"]
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False:
        ch_list = ch_loaded

    if not check_key(OPT, "COMPARE"):
        OPT["COMPARE"] = "NONE"
        rprint("[yellow]No comparison selected. Default is NONE[/yellow]")
    if OPT["COMPARE"] == "CHANNELS":
        a_list = r_list
        b_list = ch_list
    if OPT["COMPARE"] == "RUNS":
        a_list = ch_list
        b_list = r_list
    if OPT["COMPARE"] == "NONE":
        a_list = r_list
        b_list = ch_list

    data = []
    for idx, a in enumerate(a_list):
        if OPT["COMPARE"] != "NONE":
            plt.ion()
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            add_grid(ax)

        for jdx, b in enumerate(b_list):
            if OPT["COMPARE"] == "RUNS":
                run = b
                ch = a
                title = "{}".format(my_run[run][ch]["Label"]).replace(
                    "#", " "
                ) + " (Ch {})".format(ch)
                label = "Run {}".format(run)
            if OPT["COMPARE"] == "CHANNELS":
                run = a
                ch = b
                title = "Run_{} ".format(run)
                label = "{}".format(my_run[run][ch]["Label"]).replace(
                    "#", " "
                ) + " (Ch {})".format(ch)
            if OPT["COMPARE"] == "NONE":
                run = a
                ch = b
                title = "Run_{} - {}".format(run, my_run[run][ch]["Label"]).replace(
                    "#", " "
                ) + " (Ch {})".format(ch)
                label = ""

            if check_key(my_run[run][ch], "MyCuts") == False:
                # Check if RawADC is present
                if check_key(my_run[run][ch], "RawADC") == True:
                    my_run[run][ch]["MyCuts"] = np.ones(
                        len(my_run[run][ch]["RawADC"]), dtype=bool
                    )
            
            if check_key(my_run[run][ch], "UnitsDict") == False:
                get_run_units(my_run)

            if OPT["COMPARE"] == "NONE":
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                add_grid(ax)

            binning = 0
            if check_key(OPT, "ACCURACY") == True:
                binning = OPT["ACCURACY"]

            for k in key:
                # Debug the following line
                if debug:
                    rprint("[cyan]Plotting variable: %s[/cyan]" % k)
                aux_data = np.asarray(my_run[run][ch][k])[
                    np.asarray(my_run[run][ch]["MyCuts"] == True)
                ]
                aux_data = aux_data[~np.isnan(aux_data)]

                if k == "AnaPeakAmp" or k == "RawPeakAmp":
                    data = aux_data
                    if binning == 0:
                        binning = 1000

                elif k == "PeakTime":
                    data = my_run[run][ch]["Sampling"] * aux_data
                    if binning == 0:
                        binning = int(my_run[run][ch]["NBinsWvf"] / 10)

                else:
                    data = aux_data
                    ypbot = np.percentile(data, percentile[0])
                    yptop = np.percentile(data, percentile[1])
                    ypad = 0.2 * (yptop - ypbot)
                    ymin = ypbot - ypad
                    ymax = yptop + ypad
                    data = [i for i in data if ymin < i < ymax]
                    if binning == 0:
                        binning = 400  # FIXED VALUE UNTIL BETTER SOLUTION

                density = False
                y_label = "Counts"
                if check_key(OPT, "DENSITY") == True and OPT["DENSITY"] == True:
                    y_label = "Density"
                    density = True

                if select_range:
                    x1 = -1e6
                    while x1 == -1e6:
                        try:
                            x1 = float(input("xmin: "))
                            x2 = float(input("xmax: "))
                        except:
                            x1 = -1e6
                        counts, bins = np.histogram(
                            data, bins=int(binning), range=(x1, x2), density=density
                        )
                else:
                    counts, bins = np.histogram(
                        data, bins=int(binning), density=density
                    )
                
                if k == "AnaPeakAmp" or k == "RawPeakAmp":
                    dist = OPT["PEAK_DISTANCE"]
                    thresh = OPT["THRESHOLD"]
                    wdth = OPT["WIDTH"]
                    prom = OPT["PROMINENCE"]
                    counts = counts[0]
                    bins = bins[0]
                    x = np.linspace(bins[1], bins[-2], binning)
                    y_intrp = scipy.interpolate.interp1d(bins[:-1], counts)
                    y = y_intrp(x)
                    peak_idx, _ = find_peaks(y, height=thresh, width=wdth, prominence=prom, distance=dist)
                    rprint("Peaks found at: ", peak_idx)
                
                if check_key(OPT, "NORM") and OPT["NORM"]:
                    counts = counts / np.max(counts)
                    y_label = "Norm (a.u.)"

                if len(key) > 1:
                    fig.supxlabel(my_run[run][ch]["UnitsDict"][k])
                    fig.supylabel(y_label)
                    label = label + " - " + k
                    fig.suptitle(title)
                else:
                    fig.supxlabel(k + " (" + my_run[run][ch]["UnitsDict"][k] + ")")
                    fig.supylabel(y_label)
                    fig.suptitle(title + " - {} histogram".format(k))

                colors = get_prism_colors() + get_prism_colors()
                factor = 1
                if len(b_list) <= 4:
                    factor = 2
                # ax.plot(bins[:-1], counts, drawstyle = "steps", label=label, alpha = 0.95, linewidth=1.2, c=colors[1+factor*(idx+jdx)])
                ax.plot(
                    bins[:-1],
                    counts,
                    drawstyle="steps",
                    label=label,
                    alpha=0.95,
                    linewidth=1.2,
                    c=colors[int(b)],
                )

                label = label.replace(" - " + k, "")
                all_counts.append(counts)
                all_bins.append(bins)
                # all_bars.append(bars)
            if check_key(OPT, "LIMITS") and OPT["LIMITS"]:
                ax.set_xlim(OPT["XLIM"])
            if check_key(OPT, "LOGY") and OPT["LOGY"] == True:
                ax.semilogy()
            if check_key(OPT, "STATS") and OPT["STATS"] == True:
                print_stats(my_run, (run, ch, k), ax, data, info, save, debug)
            if check_key(OPT, "LEGEND") and OPT["LEGEND"]:
                 ax.legend()
            if (
                check_key(OPT, "SHOW")
                and OPT["SHOW"] == True
                and OPT["COMPARE"] == "NONE"
            ):
                plt.ion()
                plt.show()
                if (
                    check_key(OPT, "TERMINAL_MODE") == True
                    and OPT["TERMINAL_MODE"] == True
                ):
                    while not plt.waitforbuttonpress(-1):
                        pass
                    plt.close()
        if (    
            check_key(OPT, "SHOW") == True
            and OPT["SHOW"] == True
            and OPT["COMPARE"] != "NONE"
        ):
            plt.show()
            if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
                while not plt.waitforbuttonpress(-1):
                    pass
        if save:
            # Check if the directory exists
            # if not os.path.exists(
            #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/'
            # ):
            #     os.makedirs(f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/', mode=0o770, exist_ok=True)
            #     # os.chmod(f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/', 0o770)
            # fig.savefig(
            #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_{"_".join(key)}_Hist.png',
            #     dpi=500,
            # )
            
            # if OPT["COMPARE"] == "CHANNELS" and len(ch_list) > 1 :
            #     save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, f'{"_".join(key)}_Hist', debug=debug)
            # if OPT["COMPARE"] == "RUNS" and len(r_list) > 1 :
            #     save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', f'{"_".join(key)}_Hist', debug=debug)

            save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, ch, f'{"_".join(key)}_Hist', debug=debug)
            if debug:
                rprint(f"Saved figure as: run{run}_ch{ch}_{'_'.join(key)}_Hist.png")
        plt.close()

    return all_counts, all_bins


def print_stats_terminal(my_run, labels, data):
    """This function prints the statistics of the data in the terminal.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param labels: labels of the data
    :type labels: tuple
    :param data: data to analyze
    :type data: list
    
    :return: rate
    :rtype: float
    """
    
    run, ch, key = labels
    try:
        times = np.asarray(my_run[run][ch]["TimeStamp"])[
            np.asarray(my_run[run][ch]["MyCuts"] == True)
        ]
    except KeyError:
        rprint(f"[yellow]MyCuts not found! Showing stats for full data[/yellow]")
        times = np.asarray(my_run[run][ch]["TimeStamp"])

    rate = 1 / np.mean(np.diff(times))
    rprint("[cyan]\nStatistics of the histogram:[/cyan]")
    # Check if data is iterable
    if isinstance(data, (list, np.ndarray)):
        rprint("[cyan]- Counts: %i[/cyan]" % len(data))
    rprint("[cyan]- Rate: %.2E[/cyan]" % rate)
    rprint("[cyan]- Max: %.2E[/cyan]" % np.max(data))
    rprint("[cyan]- Mean: {:.2E}[/cyan]".format(np.mean(data)))
    rprint("[cyan]- Median: {:.2E}[/cyan]".format(np.median(data)))
    rprint("[cyan]- Std: {:.2E}[/cyan]".format(np.std(data)))
    
    return rate


def print_stats(my_run, labels, ax, data, info, save=False, debug=False):
    """This function prints the statistics of the data.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param labels: labels of the data
    :type labels: tuple
    :param ax: axis to plot
    :type ax: matplotlib axis
    :param data: data to analyze
    :type data: list
    :param info: info dictionary
    :type info: dict
    :param save: True if we want to save the statistics
    :type save: bool
    :param debug: True if we want to print debug messages
    :type debug: bool
    
    :return: None
    """
    
    run, ch, key = labels
    rate = print_stats_terminal(my_run, labels, data)

    # Add reference lines to the plot
    # ax.axvline(np.mean(data), label="Mean", c="k", alpha=0.5)
    # ax.axvline(np.mean(data) + np.std(data), label="STD", c="k", ls="--", alpha=0.5)
    # ax.axvline(np.mean(data) - np.std(data), c="k", ls="--", alpha=0.5)
    if save:
        df = pd.DataFrame(
            {
                "COUNTS": len(data),
                "RATE": rate,
                "MEAN": np.mean(data),
                "MEDIAN": np.median(data),
                "STD": np.std(data),
            },
            index=[0],
        )
        # Save information as csv file
        out_path = f'{root}/{info["OUT_PATH"][0]}/analysis/stats/run{run}/ch{ch}'
        if not os.path.exists(out_path):
            os.makedirs(out_path, mode=0o770, exist_ok=True)
        
        df.to_csv(
            f'{out_path}/run{run}_ch{ch}_{key}_Stats.csv',
            index=False,
        )
        if debug:
            rprint(f"Saved statistics as: run{run}_ch{ch}_{key}_Stats.csv")


def vis_two_var_hist(
    my_run,
    info,
    keys,
    percentile=[0.1, 99.9],
    select_range=False,
    OPT: Optional[dict]=None,
    save=False,
    debug=False,
):
    """This function plots two variables in a 2D histogram. Outliers are taken into account with the percentile. It plots values below and above the indicated percetiles, but values are not removed from data.
    
    :param my_run: run(s) we want to check
    :type my_run: dict
    :param info: info dictionary
    :type info: dict
    :param keys: variables we want to plot as histograms. Type: List
    :type keys: list
    :param percentile: percentile used for outliers removal
    :type percentile: list
    :param select_range: True if we want to select the range of the histogram (useful if there are many outliers)
    :type select_range: bool
    :param OPT: several options that can be True or False
        (a) DENSITY: True if we want density histograms
        (b) ACCURACY: binning of the histogram
        (c) TERMINAL_MODE: True if we want to select the channels in the terminal
        (d) COMPARE: "RUNS" to get a plot for each channel and the selected runs, "CHANNELS" to get a plot for each run and the selected channels
        (e) SHOW: True if we want to show the plot
        (f) SAVE: True if we want to save the plot
    :type OPT: dict
    :param save: True if we want to save the plot
    :type save: bool
    :param debug: True if we want to print debug messages
    :type debug: bool
    
    :return: None
    """
    
    style_selector(OPT)
    r_list = my_run["NRun"]
    ch_loaded = my_run["NChannel"]
    nevents = my_run["NEvents"]
    if type(ch_loaded) != list:
        try:
            ch_loaded = ch_loaded.tolist()
        except:
            rprint("[cyan]Imported channels as list![/cyan]")
    # Make query to user: choose loaded chanels or select specific channels
    if check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == True:
        q = [
            inquirer.Checkbox(
                "channels",
                message="Select channels to plot?",
                choices=ch_loaded,
                default=ch_loaded,
            )
        ]
        ch_list = inquirer.prompt(q)["channels"]
        
    elif check_key(OPT, "TERMINAL_MODE") == True and OPT["TERMINAL_MODE"] == False:
        ch_list = ch_loaded
    
    else:
        ch_list = ch_loaded

    if not check_key(OPT, "COMPARE"):
        OPT["COMPARE"] = "NONE"
        rprint("[yellow]No comparison selected. Default is NONE[/yellow]")
    
    if OPT["COMPARE"] == "CHANNELS":
        a_list = r_list
        b_list = ch_list
    
    if OPT["COMPARE"] == "RUNS":
        a_list = ch_list
        b_list = r_list
    
    if OPT["COMPARE"] == "NONE":
        a_list = r_list
        b_list = ch_list

    x_data = []
    y_data = []
    for run in r_list:
        for ch in ch_list:
            # if check_key(my_run[run][ch], "MyCuts") == False:
            #     generate_cut_array(my_run)
            if check_key(my_run[run][ch], "UnitsDict") == False:
                get_run_units(my_run)
    
    figures_list = []
    axes_list = []
    for a in a_list:
        for b in b_list:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            add_grid(ax)
            aux_x_data = np.zeros(nevents)
            aux_y_data = np.zeros(nevents)
            label0 = ""
            label1 = ""

            if OPT["COMPARE"] == "CHANNELS":
                title = "Run_{} ".format(a)
                if len(ch_list) > 1:
                    label0 = "{}".format(my_run[a][ch_list[0]]["Label"]).replace("#", "")
                    label1 = "{}".format(my_run[a][ch_list[1]]["Label"]).replace("#", "")
                
                    aux_x_data = my_run[a][ch_list[0]][keys[0]][
                        my_run[a][ch_list[0]]["MyCuts"] == True
                    ]
                    
                    aux_y_data = my_run[a][ch_list[1]][keys[1]][
                        my_run[a][ch_list[1]]["MyCuts"] == True
                    ]
                else:
                    rprint(f"[red][ERROR] There is only one channel in the list. Please select more than one to compare or change the settins![/red]")
            
            if OPT["COMPARE"] == "RUNS":
                title = "Channel_{} ".format(a)
                if len(r_list) > 1:
                    label0 = "{}".format(my_run[r_list[0]][a]["Label"]).replace("#", "")
                    label1 = "{}".format(my_run[r_list[1]][a]["Label"]).replace("#", "")
                
                    aux_x_data = my_run[r_list[0]][a][keys[0]][
                        my_run[r_list[0]][a]["MyCuts"] == True
                    ]
                    
                    aux_y_data = my_run[r_list[1]][a][keys[1]][
                        my_run[r_list[1]][a]["MyCuts"] == True
                    ]
                else:
                    rprint(f"[red][ERROR] There is only one run in the list. Please select more than one to compare or change the setting![/red]")

            if OPT["COMPARE"] == "NONE":
                title = "Run_{} Ch_{} - {} vs {} histogram".format(
                    a, b, keys[0], keys[1]
                )
                aux_x_data = my_run[a][b][keys[0]][my_run[a][b]["MyCuts"] == True]
                aux_y_data = my_run[a][b][keys[1]][my_run[a][b]["MyCuts"] == True]

            aux_x_data = aux_x_data[~np.isnan(aux_x_data)]
            aux_y_data = aux_y_data[~np.isnan(aux_y_data)]
            x_data = aux_x_data
            y_data = aux_y_data

            #### Calculate range with percentiles for x-axis ####
            x_ypbot = np.percentile(x_data, percentile[0])
            x_yptop = np.percentile(x_data, percentile[1])
            x_ypad = 0.2 * (x_yptop - x_ypbot)
            x_ymin = x_ypbot - x_ypad
            x_ymax = x_yptop + x_ypad

            #### Calculate range with percentiles for y-axis ####
            y_ypbot = np.percentile(y_data, percentile[0])
            y_yptop = np.percentile(y_data, percentile[1])
            y_ypad = 0.2 * (y_yptop - y_ypbot)
            y_ymin = y_ypbot - y_ypad
            y_ymax = y_yptop + y_ypad

            #### Color map choice ####
            colors = "viridis"

            if "Time" in keys[0]:
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True:
                    hist = ax.hist2d(
                        x_data * my_run[run][ch]["Sampling"],
                        y_data,
                        bins=[600, 600],
                        range=[
                            [
                                x_ymin * my_run[run][ch]["Sampling"],
                                x_ymax * my_run[run][ch]["Sampling"],
                            ],
                            [y_ymin, y_ymax],
                        ],
                        cmap=colors,
                        norm=LogNorm(),
                    )
                else:
                    hist = ax.hist2d(
                        x_data * my_run[run][ch]["Sampling"],
                        y_data,
                        bins=[600, 600],
                        range=[
                            [
                                x_ymin * my_run[run][ch]["Sampling"],
                                x_ymax * my_run[run][ch]["Sampling"],
                            ],
                            [y_ymin, y_ymax],
                        ],
                        cmap=colors,
                    )
                plt.colorbar(hist[3])
            else:
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True:
                    hist = ax.hist2d(
                        x_data,
                        y_data,
                        bins=[600, 600],
                        range=[[x_ymin, x_ymax], [y_ymin, y_ymax]],
                        cmap=colors,
                        norm=LogNorm(),
                    )
                else:
                    hist = ax.hist2d(
                        x_data,
                        y_data,
                        bins=[600, 600],
                        range=[[x_ymin, x_ymax], [y_ymin, y_ymax]],
                        cmap=colors,
                    )
                plt.colorbar(hist[3])

            ax.grid("both")
            fig.supxlabel(
                label0
                + " "
                + keys[0]
                + " ("
                + my_run[run][ch]["UnitsDict"][keys[0]]
                + ")"
            )
            fig.supylabel(
                label1
                + " "
                + keys[1]
                + " ("
                + my_run[run][ch]["UnitsDict"][keys[1]]
                + ")"
            )
            fig.suptitle(title)
            if select_range:
                x1 = -1e6
                while x1 == -1e6:
                    try:
                        x1 = float(input("xmin: "))
                        x2 = float(input("xmax: "))
                        y1 = float(input("ymin: "))
                        y2 = float(input("ymax: "))
                    except:
                        x1 = -1e6
                if check_key(OPT, "LOGZ") == True and OPT["LOGZ"] == True:
                    hist = ax.hist2d(
                        x_data,
                        y_data,
                        bins=[300, 300],
                        range=[[x1, x2], [y1, y2]],
                        cmap=colors,
                        norm=LogNorm(),
                    )
                else:
                    hist = ax.hist2d(
                        x_data,
                        y_data,
                        bins=[300, 300],
                        range=[[x1, x2], [y1, y2]],
                        cmap=colors,
                    )
                plt.colorbar(hist[3])
                ax.grid("both")

            figures_list.append(fig)
            axes_list.append(ax)
            if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                plt.yscale("log")
            if save == True:
                # fig.savefig(
                #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_{keys[0]}_{keys[1]}_Hist2D.png',
                #     dpi=500,
                # )
                # os.chmod(
                #     f'{root}/{info["OUT_PATH"][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_{keys[0]}_{keys[1]}_Hist2D.png',
                #     stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
                # )
                save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images', run, ch, f'{keys[0]}_{keys[1]}_Hist2D', debug=debug)
                if debug:
                    rprint(
                        f"Saved figure as: run{run}_ch{ch}_{keys[0]}_{keys[1]}_Hist2D.png"
                    )

            # Save to specific folder determined by OPT
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
                plt.ion()
                plt.show()
                while not plt.waitforbuttonpress(-1):
                    pass
                plt.close()
            if OPT["COMPARE"] != "NONE":
                break

    return figures_list, axes_list
