# ================================================================================================================================================#
# This library contains function to perform the calibration of our sensors. They are mostly used in the 04Calibration.py macro.                  #
# ================================================================================================================================================#
from srcs.utils import get_project_root

import scipy, os, stat, yaml
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("Qt5Agg")

from jacobi import propagate
from matplotlib.colors import LogNorm
from matplotlib.cm import viridis
from itertools import product
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from scipy.optimize import curve_fit

# Import from other libraries
from .io_functions import check_key, write_output_file, save_figure
from .head_functions import update_yaml_file
from .ana_functions import (
    get_run_units,
    get_wvf_label,
    compute_ana_wvfs,
)
from .cut_functions import generate_cut_array
from .fig_config import figure_features, add_grid
from .fit_functions import (
    gaussian_train_fit,
    gaussian_train,
    pmt_spe_fit,
    gaussian_fit,
    gaussian,
    peak_valley_finder,
    PoissonPlusBinomial,
)
from .vis_functions import vis_var_hist
from .sty_functions import style_selector, get_prism_colors, get_color

root = get_project_root()


def vis_persistence(my_run, info, OPT, save=False, debug=False):
    """This function plot the PERSISTENCE histogram of the given runs&ch. It perfoms a cut in 20<"PeakTime"(bins)<50 so that all the events not satisfying the condition are removed. Binning is fixed (x=5000, y=1000) [study upgrade]. X_data (time) and Y_data (waveforms) are deleted after the plot to save space. WARNING! flattening long arrays leads to MEMORY problems :/.
    
    :param my_run: run(s) we want to check.
    :type my_run: dict
    :param info: dictionary with the information of the run.
    :type info: dict
    :param OPT: several options that can be True or False.
    :type OPT: dict
    :param save: if True, it will save the plot in the images folder.
    :type save: bool
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    """

    style_selector(OPT)
    plt.ion()
    true_key, true_label = get_wvf_label(my_run, "", "", debug=debug)
    rprint("[magenta]True key: %s[/magenta]" % true_key)
    rprint("[magenta]True label: %s[/magenta]" % true_label)
    if true_key == "RawADC":
        rprint("\nAnaADC not saved but we compute it now :)", "WARNING")
        compute_ana_wvfs(my_run, info, debug=debug)
        key = "AnaADC"
    else:
        key = true_key

    for run, ch in product(my_run["NRun"], my_run["NChannel"]):
        if check_key(my_run[run][ch], "MyCuts") == False:
            generate_cut_array(my_run, debug=debug)
        data_flatten = my_run[run][ch][key][
            np.where(my_run[run][ch]["MyCuts"] == True)
        ].flatten()  ##### Flatten the data array
        time = my_run[run][ch]["Sampling"] * np.arange(
            len(my_run[run][ch][key][0])
        )  # Time array
        time_flatten = np.array([time] * int(len(data_flatten) / len(time))).flatten()

        fig = plt.figure()
        plt.hist2d(
            time_flatten,
            data_flatten,
            density=True,
            bins=[5000, 1000],
            cmap=viridis,
            norm=LogNorm(),
        )
        plt.colorbar()
        plt.grid(True, alpha=0.7)  # , zorder = 0 for grid behind hist
        plt.title("Run_{} Ch_{} - Persistence".format(run, ch), size=14)
        plt.xticks(size=11)
        plt.yticks(size=11)
        plt.xlabel("Time [s]", size=11)
        plt.ylabel("Amplitude [ADC]", size=11)
        
        if OPT["XLIM"] != False:
            plt.xlim(OPT["XLIM"])
        
        if OPT["YLIM"] != False:
            plt.ylim(OPT["YLIM"])
        
        if OPT["LOGX"] == True:
            plt.xscale("log")
        
        if OPT["LOGY"] == True:
            plt.yscale("log")
        
        if save:
            save_figure(fig, f"{info['OUT_PATH'][0]}/images", run, ch, "Persistence", debug=debug)
            # plt.savefig(
            #     f"{info['OUT_PATH'][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_Persistence.png",
            #     dpi=500,
            # )
        
        del data_flatten, time, time_flatten
        while not plt.waitforbuttonpress(-1):
            pass
        plt.clf()
    plt.ioff()
    plt.clf()


def calibrate(my_runs, info, keys, OPT={}, save=False, debug=False):
    """Computes calibration hist of a collection of runs. A fit is performed (train of gaussians) and we have as a return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    
    :param my_runs: run(s) we want to check.
    :type my_runs: dict
    :param info: dictionary with the information of the run.
    :type info: dict
    :param keys: variables we want to plot as histograms.
    :type keys: list
    :param OPT: several options that can be True or False.
      (a) LOGY: True if we want logarithmic y-axis
      (b) SHOW: if True, it will show the calibration plot
    :type OPT: dict
    :param save: if True, it will save the plot in the images folder.
    :type save: bool
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: calibration
    :rtype: dict
    """
    
    calibration = dict()
    style_selector(OPT)
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):
        calibration[(run, ch, key)] = dict()
        if len(my_runs[run][ch].keys()) == 0:
            rprint("\n RUN DOES NOT EXIST. Looking for the next", "WARNING")
            popt = [-99, -99, -99]
            pcov = [-99, -99, -99]

        else:
            det_label = my_runs[run][ch]["Label"]
            if check_key(my_runs[run][ch], "MyCuts") == False:
                rprint("Cuts not generated. Generating them now...", "WARNING")
                generate_cut_array(
                    my_runs, debug=debug
                )  # If cuts not generated, generate them

            if check_key(my_runs[run][ch], "UnitsDict") == False:
                get_run_units(my_runs)  # Get units

            OPT["SHOW"] == False
            counts, bins = vis_var_hist(
                my_runs, info=info, key=[key], OPT=OPT, percentile=[1, 99]
            )
            counts = counts[0]
            bins = bins[0]

            ## New Figure with the fit ##
            plt.ion()
            plt.rcParams.update({"font.size": 16})
            fig_cal, ax_cal = plt.subplots(1, 1, figsize=(8, 6))
            # Add histogram from vis_var_hist
            center_bins = (bins[:-1] + bins[1:]) / 2
            ax_cal.hist(
                center_bins,
                bins,
                weights=counts,
                histtype="step",
                label=key,
                align="left",
                lw=2,
                color=get_color(ch, even=True, debug=debug),
            )
            fig_cal.suptitle("Run_{} Ch_{} - {} histogram".format(run, ch, key))
            fig_cal.supxlabel(key + " (" + my_runs[run][ch]["UnitsDict"][key] + ")")
            fig_cal.supylabel("Counts")
            add_grid(ax_cal)

            popt, pcov = calibration_fit_plot(ax_cal, counts, bins, OPT, debug=debug)
            data = {(run, ch, key): {"CALIB": {"popt": popt, "pcov": pcov}}}
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
                plt.show()
                while not plt.waitforbuttonpress(-1):
                    pass
                plt.close()
            export_txt(data, info, debug=debug)

            fig_xt, ax_xt = plt.subplots(1, 1, figsize=(8, 6))
            fig_xt.suptitle("Run_{} Ch_{} - {} Vinogradov X-Talk".format(run, ch, key))
            fig_xt.supxlabel("PE")
            fig_xt.supylabel("Counts (density)")
            add_grid(ax_xt)

            xt_popt, xt_pcov = xtalk_fit_plot(
                ax_xt, popt, (run, ch, key), OPT, debug=debug
            )
            data = {(run, ch, key): {"XTALK": {"popt": xt_popt, "pcov": xt_pcov}}}
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
                plt.show()
                while not plt.waitforbuttonpress(-1):
                    pass
                plt.close()
            export_txt(data, info, debug=debug)

            if save:
                save_path = f'{root}/{info["OUT_PATH"][0]}/images/'
                try:
                    os.makedirs(f"{save_path}run{run}/ch{ch}", mode=0o777, exist_ok=True)
                
                except:
                    rprint(f"[yellow][WARNING] Folder {save_path} already exists. No need to create it.[/yellow]")
                
                save_figures(fig_cal, fig_xt, (run, ch, key), save_path, debug=debug)

            try:
                my_runs[run][ch]["Gain"] = popt[3] - abs(popt[0])
                my_runs[run][ch]["AnaMaxChargeNoise"] = (
                    popt[0] + (popt[3] - popt[0]) / 2
                )
                my_runs[run][ch]["AnaMinChargeNoise"] = (
                    popt[0] - (popt[3] - popt[0]) / 2
                )
                my_runs[run][ch]["AnaMaxChargeSPE"] = popt[3] + (popt[6] - popt[3]) / 2
                my_runs[run][ch]["AnaMinChargeSPE"] = popt[3] - (popt[3] - popt[0]) / 2
            except IndexError:
                rprint(
                    "Fit failed to find min of 3 calibration peaks!", "WARNING"
                )
                my_runs[run][ch]["Gain"] = -99
                my_runs[run][ch]["AnaMaxChargeNoise"] = -99
                my_runs[run][ch]["AnaMinChargeNoise"] = -99
                my_runs[run][ch]["AnaMaxChargeSPE"] = -99
                my_runs[run][ch]["AnaMinChargeSPE"] = -99

        calibration[(run, ch, key)]["XTALK"] = {"popt": xt_popt, "pcov": xt_pcov}
        calibration[(run, ch, key)]["CALIB"] = {"popt": popt, "pcov": pcov}

    return calibration


def calibration_fit_plot(ax_cal, counts, bins, OPT, debug=False):
    """This function performs the calibration fit and plots the results.
    
    :param ax_cal: axis to plot the calibration fit.
    :type ax_cal: matplotlib axis
    :param counts: counts of the histogram.
    :type counts: nparray
    :param bins: bins of the histogram.
    :type bins: nparray
    :param OPT: several options that can be True or False.
    :type OPT: dict
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: popt, pcov
    :rtype: tuple
    """
    
    new_params = {}
    params = {
        "THRESHOLD": 0.1,
        "WIDTH": 5,
        "PROMINENCE": 0.01,
        "PEAK_DISTANCE": 20,
        "ACCURACY": 1000,
        "FIT": "gaussian",
    }
    for i, param in enumerate(list(params.keys())):
        if check_key(OPT, param) == True:
            new_params[param] = OPT[param]
        else:
            new_params[param] = params[param]

    x = np.linspace(bins[1], bins[-2], params["ACCURACY"])
    y_intrp = scipy.interpolate.interp1d(bins[:-1], counts)
    y = y_intrp(x)

    peak_idx, valley_idx = peak_valley_finder(x, y, new_params)
    ax_cal.axhline(np.max(y) * new_params["THRESHOLD"], ls="--")
    ax_cal.plot(x[peak_idx], y[peak_idx], "r.", lw=4, label="Peaks")
    ax_cal.plot(x[valley_idx], y[valley_idx], "b.", lw=6, label="Valleys")

    popt, pcov = gaussian_train_fit(
        ax_cal,
        x=x,
        y=y,
        y_intrp=y_intrp,
        peak_idx=peak_idx,
        valley_idx=valley_idx,
        params=new_params,
        debug=debug,
    )
    ax_cal.plot(x, gaussian_train(x, *popt), label="Final fit", color="red")

    if check_key(OPT, "LEGEND") == True and OPT["LEGEND"] == True:
        ax_cal.legend()

    if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
        ax_cal.semilogy()
        ax_cal.set_ylim(1)

    try:
        popt = popt.tolist()
        pcov = pcov.tolist()
    except AttributeError:
        pass
    return popt, pcov


def xtalk_fit_plot(ax_xt, popt, labels, OPT, debug=False):
    """This function performs the xtalk fit and plots the results.
    
    :param ax_xt: axis to plot the xtalk fit.
    :type ax_xt: matplotlib axis
    :param popt: best fit parameters.
    :type popt: nparray
    :param labels: labels of the histogram.
    :type labels: tuple
    :param OPT: several options that can be True or False.
    :type OPT: dict
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: xt_popt, xt_pcov
    :rtype: tuple
    """
    
    run, ch, key = labels
    PNs = popt[1::3] * np.abs(popt[2::3]) / sum(popt[1::3] * np.abs(popt[2::3]))
    PNs_err = (popt[1::3] * np.abs(popt[2::3])) ** 0.5 / sum(
        popt[1::3] * np.abs(popt[2::3])
    )

    if len(PNs) > 5:
        rprint(
            f"[yellow]More than 5 peaks found. Using the first {len(PNs)} peaks for the fit.[/yellow]"
        )
        PNs = PNs[:-1]
        PNs = PNs / np.sum(PNs)
        PNs_err = PNs_err[:-1]

    l = -np.log(PNs[0])
    p = 1 - PNs[1] / (l * PNs[0])
    xdata = np.arange(len(PNs))

    ax_xt.bar(
        np.array(xdata),
        PNs,
        label="Data",
        width=0.4,
        color=get_color(ch, even=True, debug=debug),
    )
    # Add vertical line to mean value
    mean = np.sum(np.array(xdata) * PNs) / np.sum(np.array(xdata))
    ax_xt.axvline(
        x=mean,
        color="black",
        linestyle="--",
        label=f"Mean value: {mean:.2f}",
    )
    try:
        xt_popt, xt_pcov = curve_fit(
            PoissonPlusBinomial,
            xdata,
            PNs,
            sigma=PNs_err,
            p0=[len(PNs), p, l],
            bounds=([len(PNs) - 1e-12, 0, 0], [len(PNs) + 1e-12, 1, 10]),
        )
        ax_xt.plot(
            xdata,
            PoissonPlusBinomial(xdata, *xt_popt),
            "x",
            label="Fit: CT = "
            + str(int(xt_popt[1] * 100))
            + "% - "
            + r"$\lambda = {:.2f}$".format(xt_popt[2]),
            color="red",
        )
    except:
        rprint("Fit failed. Returning initial parameters.", "WARNING")
        xt_popt = np.asarray([len(PNs), p, l])
        xt_pcov = np.asarray([-99, -99, -99])
        # ax_xt.plot(xdata, PoissonPlusBinomial(xdata, *xt_popt), 'x', label="Fit: CT = " + str(int(xt_popt[1] * 100)) + "% - " + r'$\lambda = {:.2f}$'.format(xt_popt[2]), color="red")

    if check_key(OPT, "LEGEND") == True and OPT["LEGEND"] == True:
        ax_xt.legend()

    return xt_popt.tolist(), xt_pcov.tolist()


def export_txt(data: dict, info: dict, debug: bool = False) -> None:
    """This function exports the calibration and xtalk data to a txt file.
    
    :param data: data to be exported.
    :type data: dict
    :param info: dictionary with the information of the run.
    :type info: dict
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: None
    """
    
    for labels in data:
        run, ch, key = labels
        for measurement in data[labels]:
            if measurement == "CALIB":
                popt, pcov = (
                    data[labels][measurement]["popt"],
                    data[labels][measurement]["pcov"],
                )
                export = calibration_txt(run, ch, key, popt, pcov, info, debug=debug)
                # If export dump data to yml file
                if export:
                    rprint("[cyan]Data exported to txt file.[/cyan]")
                    update_yaml_file(
                        f'{root}/{info["OUT_PATH"][0]}/analysis/calibration/run{run}/ch{ch}/calibration_run{run}_ch{ch}_{key}.yml',
                        data[labels][measurement],
                        debug=debug,
                    )

            if measurement == "XTALK":
                xt_popt, xt_pcov = (
                    data[labels][measurement]["popt"],
                    data[labels][measurement]["pcov"],
                )
                export = xtalk_txt(run, ch, key, xt_popt, xt_pcov, info, debug=debug)
                # If export dump data to yml file
                if export:
                    rprint("[cyan]Data exported to txt file.[/cyan]")
                    update_yaml_file(
                        f'{root}/{info["OUT_PATH"][0]}/analysis/xtalk/run{run}/ch{ch}/xtalk_run{run}_ch{ch}_{key}.yml',
                        data[labels][measurement],
                        debug=debug,
                    )


def calibration_txt(run, ch, key, popt, pcov, info, debug=False) -> bool:
    """Computes calibration parameters.
    
    :param run: run number.
    :type run: int
    :param ch: channel number.
    :type ch: int
    :param key: key of the histogram.
    :type key: str
    :param popt: best fit parameters.
    :type popt: nparray
    :param pcov: covariance matrix.
    :type pcov: nparray
    :param info: dictionary with the information of the run.
    :type info: dict
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: export
    :rtype: bool
    """

    if all(x != -99 for x in popt):
        cal_parameters = []
        perr = np.sqrt(np.diag(pcov))  # error for each variable
        fitted_peaks = int(len(popt) / 3)  # three parameters fitted for each peak
        for i in np.arange(fitted_peaks):
            mu = [popt[(i + 0) + 2 * i], perr[(i + 0) + 2 * i]]  # mu +- dmu
            height = [
                popt[(i + 1) + 2 * i],
                perr[(i + 1) + 2 * i],
            ]  # height +- dheight (not saving in txt by default)
            sigma = [popt[(i + 2) + 2 * i], perr[(i + 2) + 2 * i]]  # sigma +- dsigma
            cal_parameters.append([mu, height, sigma])
            copy_cal = cal_parameters

        for i in np.arange(fitted_peaks):  # distances between peaks
            if i == fitted_peaks - 1:
                gain = -99
                dgain = -99
                sn0 = -99
                dsn0 = -99
                sn1 = -99
                dsn1 = -99
                sn2 = -99
                dsn2 = -99
            else:
                gain = copy_cal[i + 1][0][0] - copy_cal[i][0][0]
                dgain = np.sqrt(
                    copy_cal[i + 1][0][1] ** 2 + copy_cal[i][0][1] ** 2
                )  # *1e-12/1.602e-19 #when everythong was pC

                sn0 = (copy_cal[i + 1][0][0] - copy_cal[i][0][0]) / copy_cal[i][2][0]
                dsn0 = sn0 * np.sqrt(
                    (
                        (copy_cal[i + 1][0][1] ** 2 + copy_cal[i][0][1] ** 2)
                        / ((copy_cal[i + 1][0][0] - copy_cal[i][0][0]))
                    )
                    ** 2
                    + (copy_cal[i][2][1] / copy_cal[i][2][0]) ** 2
                )

                sn1 = (copy_cal[i + 1][0][0] - copy_cal[i][0][0]) / copy_cal[i + 1][2][
                    0
                ]
                dsn1 = sn1 * np.sqrt(
                    (
                        (copy_cal[i + 1][0][1] ** 2 + copy_cal[i][0][1] ** 2)
                        / ((copy_cal[i + 1][0][0] - copy_cal[i][0][0])) ** 2
                    )
                    + (copy_cal[i + 1][2][1] / copy_cal[i + 1][2][0]) ** 2
                )

                sn2 = (copy_cal[i + 1][0][0] - copy_cal[i][0][0]) / (
                    np.sqrt(copy_cal[i][2][0] ** 2 + copy_cal[i + 1][2][0] ** 2)
                )
                dsn2 = sn2 * np.sqrt(
                    (dgain / gain) ** 2
                    + (
                        (copy_cal[i][2][0] * copy_cal[i][2][1])
                        / ((copy_cal[i][2][0]) ** 2 + (copy_cal[i + 1][2][0]) ** 2)
                    )
                    ** 2
                    + (
                        (copy_cal[i + 1][2][0] * copy_cal[i + 1][2][1])
                        / ((copy_cal[i][2][0]) ** 2 + (copy_cal[i + 1][2][0]) ** 2)
                    )
                    ** 2
                )

            cal_parameters[i].append([gain, dgain])
            cal_parameters[i].append([sn0, dsn0])
            cal_parameters[i].append([sn1, dsn1])
            cal_parameters[i].append([sn2, dsn2])

        fitted_peaks = len(cal_parameters)
        for i in np.arange(fitted_peaks):  # three parameters fitted for each peak
            console = Console()
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Parameter")
            table.add_column("Value")
            table.add_column("Error")

            parameters = ["MU", "HEIGHT", "SIGMA", "GAIN", "SN0", "SN1", "SN2"]
            for j, parameter in enumerate(parameters):
                value, error = "{:.2E}".format(
                    cal_parameters[i][j][0]
                ), "{:.2E}".format(cal_parameters[i][j][1])
                table.add_row(parameter, value, error)

            console.rprint("\nPeak:", i)
            console.rprint(table)

        export = write_output_file(
            run,
            ch,
            cal_parameters,
            f"Calibration_{key}_",
            info,
            write_mode="w",
            header_list=[
                "MU",
                "DMU",
                "SIG",
                "DSIG",
                "GAIN",
                "DGAIN",
                "SN0",
                "DSN0",
                "SN1",
                "DSN1",
                "SN2",
                "DSN2",
            ],
        )
        return export


def xtalk_txt(run, ch, key, xt_popt, xt_pcov, info, debug=False) -> bool:
    """Computes xtalk parameters.
    
    :param run: run number.
    :type run: int
    :param ch: channel number.
    :type ch: int
    :param key: key of the histogram.
    :type key: str
    :param xt_popt: best fit parameters.
    :type xt_popt: nparray
    :param xt_pcov: covariance matrix.
    :type xt_pcov: nparray
    :param info: dictionary with the information of the run.
    :type info: dict
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: export
    :rtype: bool
    """
    xt_parameters = []
    xt_perr = np.sqrt(np.diag(xt_pcov))  # error for each variable

    npeaks = [xt_popt[0], xt_perr[0]]
    xt = [xt_popt[1], xt_perr[1]]
    l = [xt_popt[2], xt_perr[2]]
    xt_parameters.append([npeaks, xt, l])

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Parameter")
    table.add_column("Value")
    table.add_column("Error")
    parameters = ["NPEAK", "XT", "LAMBDA"]
    for j, parameter in enumerate(parameters):
        try:
            value, error = "{:.2f}".format(xt_parameters[0][j][0]), "{:.2f}".format(
                xt_parameters[0][j][1]
            )
            table.add_row(parameter, value, error)
        except TypeError:
            table.add_row(parameter, "N/A", "N/A")
    console.rprint("\nX-Talk:")
    console.rprint(table)

    export = write_output_file(
        run,
        ch,
        xt_parameters,
        f"XTalk_{key}_",
        info,
        write_mode="w",
        header_list=["NPEAK", "XT", "DXT", "LAMBDA", "DLAMBDA"],
        not_saved=[1],
    )
    return export


def get_gains(run, channels, folder_path="TUTORIAL", debug=False):
    """This function reads the gains from the txt files.
    
    :param run: run number.
    :type run: int
    :param channels: channels to read the gains from.
    :type channels: list
    :param folder_path: path to the folder where the gains are stored.
    :type folder_path: str
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: gains, Dgain
    :rtype: dict, dict
    """
    
    gains = dict.fromkeys(channels)
    Dgain = dict.fromkeys(channels)
    for c, ch in enumerate(channels):
        my_table = pd.read_csv(
            folder_path + "/analysis/fits/run%i/ch%i/gain_ch%i.txt" % (run, ch, ch),
            header=None,
            sep="\t",
            usecols=np.arange(16),
            names=[
                "RUN",
                "OV",
                "PEAK",
                "MU",
                "DMU",
                "SIG",
                "DSIG",
                "\t",
                "GAIN",
                "DGAIN",
                "SN0",
                "DSN0",
                "SN1",
                "DSN1",
                "SN2",
                "DSN2",
            ],
        )
        my_table = my_table.iloc[1:]
        gains[ch] = list(
            np.array(my_table["GAIN"]).astype(float)[my_table["RUN"] == str(run)]
        )
        Dgain[ch] = list(
            np.array(my_table["DGAIN"]).astype(float)[my_table["RUN"] == str(run)]
        )
        # if debug: rprint("\nGAIN TXT FOR CHANNEL %i"%ch ); display(my_table)

    return gains, Dgain


def scintillation_txt(run, ch, key, popt, pcov, filename, info):
    """Computes charge parameters. Given popt and pcov which are the output for the best parameters when performing the Gaussian fit.
    
    :param run: run number.
    :type run: int
    :param ch: channel number.
    :type ch: int
    :param key: key of the histogram.
    :type key: str
    :param popt: best fit parameters.
    :type popt: nparray
    :param pcov: covariance matrix.
    :type pcov: nparray
    :param filename: name of the file to save the parameters.
    :type filename: str
    :param info: dictionary with the information of the run.
    :type info: dict
    
    :return: export
    :rtype: bool
    """

    charge_parameters = []
    perr0 = np.sqrt(np.diag(pcov))  # error for each variable
    # perr1 = np.sqrt(np.diag(pcov[1]))  #error for each variable

    mu = [popt[1], perr0[1]]  # mu +- dmu
    height = [popt[0], perr0[0]]  # height +- dheight (not saving in txt by default)
    sigma = [abs(popt[2]), perr0[2]]  # sigma +- dsigma
    charge_parameters.append([mu, height, sigma])

    rprint(len(charge_parameters))
    rprint(charge_parameters)

    rprint("MU +- DMU:", ["{:.2f}".format(item) for item in charge_parameters[0][0]])
    rprint(
        "HEIGHT +- DHEIGHT:",
        ["{:.2f}".format(item) for item in charge_parameters[0][1]],
    )
    rprint(
        "SIGMA +- DSIGMA:", ["{:.2f}".format(item) for item in charge_parameters[0][2]]
    )

    export = write_output_file(
        run,
        ch,
        charge_parameters,
        filename + key,
        info,
        header_list=["RUN", "OV", "PEAK", "MU", "DMU", "SIG", "DSIG"],
    )


def charge_fit(my_runs, keys, OPT={}):
    """Computes charge hist of a collection of runs. A fit is performed (1 gaussian) and we have as a return the popt, pcov, perr for the best fitted parameters. Not only that but a plot is displayed.
    
    :param my_runs: run(s) we want to check.
    :type my_runs: dict
    :param keys: variables we want to plot as histograms.
    :type keys: list
    :param OPT: several options that can be True or False.
      (a) LOGY: True if we want logarithmic y-axis
      (b) SHOW: if True, it will show the calibration plot
    :type OPT: dict
    
    :return: all_popt, all_pcov, all_perr
    :rtype: list, list, list
    """

    next_plot = False
    counter = 0
    all_counts, all_bins, all_bars = vis_var_hist(my_runs, keys, OPT=OPT)
    all_popt = []
    all_pcov = []
    all_perr = []
    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], keys):

        if check_key(my_runs[run][ch], "MyCuts") == False:
            generate_cut_array(my_runs)  # if no cuts, generate them
        if check_key(my_runs[run][ch], "UnitsDict") == False:
            get_run_units(my_runs)  # if no units, generate them
        # try:
        thresh = int(len(my_runs[run][ch][key]) / 1000)

        ## New Figure with the fit ##
        plt.ion()
        fig_ch, ax_ch = plt.subplots(1, 1, figsize=(8, 6))
        add_grid(ax_ch)
        counts = all_counts[counter]
        bins = all_bins[counter]
        bars = all_bars[counter]
        ax_ch.hist(bins[:-1], bins, weights=counts, histtype="step")
        fig_ch.suptitle("Run_{} Ch_{} - {} histogram".format(run, ch, key))
        fig_ch.supxlabel(key + " (" + my_runs[run][ch]["UnitsDict"][key] + ")")
        fig_ch.supylabel("Counts")

        ### --- 1x GAUSSIAN FIT --- ###
        x, popt, pcov, perr = gaussian_fit(
            counts, bins, bars, thresh, fit_function="gaussian"
        )
        rprint(
            "Chi2/N?: ",
            (
                sum(
                    (
                        my_runs[run][ch][key]
                        - gaussian(
                            my_runs[run][ch]["Sampling"]
                            * np.arange(len(my_runs[run][ch][key])),
                            *popt,
                        )
                    )
                    ** 2
                )
            )
            / len(my_runs[run][ch][key]),
        )
        ax_ch.plot(x, gaussian(x, *popt), label="")

        if check_key(OPT, "LEGEND") == True and OPT["LEGEND"] == True:
            ax_ch.legend()
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
            ax_ch.semilogy()
            plt.ylim(ymin=1, ymax=1.2 * max(counts))

        ## Repeat customized fit ##
        confirmation = input("Are you happy with the fit? (y/n) ")
        if "n" in confirmation:
            rprint(
                "\n--- Repeating the fit with input parameters (\u03BC \u00B1 \u03C3) \u03B5 [{:0.2f}, {:0.2f}] ---".format(
                    x[0], x[-1]
                )
            )
            mean = input("Introduce MEAN value for the fit: ")
            sigma = input("Introduce SIGMA value for the fit: ")

            x, popt, pcov, perr = gaussian_fit(
                counts, bins, bars, thresh, custom_fit=[float(mean), float(sigma)]
            )
            ax_ch.plot(x, gaussian(x, *popt), label="")
            all_popt.append(popt)
            all_pcov.append(pcov)
            all_perr.append(perr)
        else:
            all_popt.append(popt)
            all_pcov.append(pcov)
            all_perr.append(perr)
            plt.close()
            continue

        if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
            while not plt.waitforbuttonpress(-1):
                pass
        counter += 1
        plt.close()
        # except KeyError:
        #     rprint("Empty dictionary. No computed charge.")

    return all_popt, all_pcov, all_perr


def save_figures(fig_cal, fig_xt, labels, save_path, debug=False):
    """Saves the figures in the images folder.
    
    :param fig_cal: figure of the calibration.
    :type fig_cal: matplotlib figure
    :param fig_xt: figure of the xtalk.
    :type fig_xt: matplotlib figure
    :param labels: labels of the histogram.
    :type labels: tuple
    :param save_path: path to the folder where the images are stored.
    :type save_path: str
    :param debug: if True, it will display the debug messages.
    :type debug: bool
    
    :return: None
    """
    
    run, ch, key = labels
    # Check if the folder exists, if not create it
    try:
        os.makedirs(f"{save_path}run{run}/ch{ch}", mode=0o777, exist_ok=True)
    except:
        rprint(
            f"[yellow][WARNING] Folder {save_path}run{run}/ch{ch} already exists. No need to create it.[/yellow]"
        )
    fig_cal.savefig(f"{save_path}run{run}/ch{ch}/run{run}_ch{ch}_{key}_Hist.png", dpi=500)
    fig_xt.savefig(f"{save_path}run{run}/ch{ch}/run{run}_ch{ch}_{key}_XTalk.png", dpi=500)
    try:
        os.chmod(
            f"{save_path}run{run}/ch{ch}/run{run}_ch{ch}_{key}_Hist.png",
            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
        )
        os.chmod(
            f"{save_path}run{run}/ch{ch}/run{run}_ch{ch}_{key}_XTalk.png",
            stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO,
        )
    except:
        rprint(
            f"File permissions could not be changed. Check if the file exists & if you have permissions change them manually."
        )
    if debug:
        rprint(f"Saved figure as: run{run}_ch{ch}_{key}_Hist.png")
        rprint(f"Saved figure as: run{run}_ch{ch}_{key}_XTalk.png")
