# ================================================================================================================================================#
# This library contains functions to perform deconvolution to our waveforms.                                                                     #
# ================================================================================================================================================#

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import scipy.interpolate
from scipy.optimize import curve_fit
from itertools import product
from rich import print as rprint
from rich.progress import track

# Imports from other libraries
from .io_functions import check_key, save_figure
from .fit_functions import dec_gauss, fit_dec_gauss
from .ana_functions import compute_power_spec, find_amp_decrease, find_baseline_cuts, smooth


def generate_SER(my_runs, light_runs, SPE_runs, scaling_type="Amplitude", debug=False):
    """This function rescales AveWvfs from light runs to SPE level to be used for wvf deconvolution.
    
    :param my_runs: dictionary containing the wvf to be deconvolved
    :type my_runs: dict
    :param light_runs: dictionary containing the wvfs that work as detector response (light runs)
    :type light_runs: dict
    :param SPE_runs: dictionary containing the SPE wvf that serve as reference to rescale dec_runs
    :type SPE_runs: dict
    :param scaling_type: type of scaling to be used, defaults to "Amplitude"
    :type scaling_type: str, optional
    :param debug: debug flag, defaults to False
    :type debug: bool, optional
    """

    for ii in range(len(my_runs["NRun"])):
        for jj in range(len(my_runs["NChannel"])):
            try:
                det_response = light_runs[light_runs["NRun"][0]][
                    my_runs["NChannel"][jj]
                ]["AnaAveWvf"][0]
            except KeyError:
                exit(
                    f"Key error in light run: run {my_runs['NRun'][ii]} channel {my_runs['NChannel'][jj]} key AnaAveWvf"
                )
            try:
                single_response = SPE_runs[SPE_runs["NRun"][0]][
                    my_runs["NChannel"][jj]
                ]["AnaAveWvfSPE"][0]
            except KeyError:
                exit(
                    f"Key error in calib run: run {my_runs['NRun'][ii]} channel {my_runs['NChannel'][jj]} key AnaAveWvfSPE"
                )

            if scaling_type == "Amplitude":
                SER = np.max(single_response) * det_response / np.max(det_response)
            if scaling_type == "Area":
                SER = np.sum(single_response) * det_response / np.sum(det_response)

            i_idx, f_idx = find_amp_decrease(SER, 1e-4)
            SER = np.roll(SER, -i_idx)
            my_runs[my_runs["NRun"][ii]][my_runs["NChannel"][jj]]["AnaAveWvfSER"] = [
                SER
            ]

    if debug:
        rprint("[green]\n---SER generated![/green]")


def deconvolve(my_runs, info, keys=[], noise_run=[], peak_buffer=20, OPT={}, debug=False):
    """This function deconvolves any given number of arrays according to a provided SPE template.
    
    :param my_runs: dictionary containing the wvf to be deconvolved
    :type my_runs: dict
    :param info: dictionary containing the output path
    :type info: dict
    :param keys: list containing the keys of [wvf, template, outputkey]
    :type keys: list
    :param noise_run: dictionary containing the noise run
    :type noise_run: dict
    :param peak_buffer: left distance from peak to calculate baseline
    :type peak_buffer: int
    :param OPT: dictionary with settings and vis options ("SHOW", "LOGY", "NORM", "FILTER": Gauss/Wiener, etc.).
    :type OPT: dict
    :param debug: debug flag, defaults to False
    :type debug: bool, optional
    """

    for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
        aux = []
        trimm = 0
        template = my_runs[run][ch][keys[1]][0]

        # Use a track for loop to print a progress bar
        for i in track(
            range(len(my_runs[run][ch][keys[0]])), description="Processing..."
        ):
            # Select required runs and parameters
            signal = my_runs[run][ch][keys[0]][i]
            if "Raw" in keys[0]:
                label = "Raw"
                signal = my_runs[run][ch]["PChannel"] * (
                    signal - my_runs[run][ch][label + "PedMean"][i]
                )
            # Arrays must be even for fft
            signal = check_array_even(signal)
            template = check_array_even(template)

            # Arrays must have the same length
            template, signal = check_array_len(template, signal)

            # Roll signal to align wvfs
            # template = np.roll(template, np.argmax(signal)-np.argmax(template))

            # Can be used for test to trimm array
            if check_key(OPT, "TRIMM") == True:
                trimm = OPT["TRIMM"]
            if check_key(OPT, "AUTO_TRIMM") == True and OPT["AUTO_TRIMM"] == True:
                j = 0
                while 2**j < len(signal):
                    j = j + 1
                trimm = len(signal) - 2 ** (j - 1)

            # rprint(template)
            if check_key(OPT, "SMOOTH") == True:
                if OPT["SMOOTH"] > 0:
                    signal = smooth(signal, OPT["SMOOTH"])
                else:
                    rprint("[red]Invalid value encountered in smooth[/red]")

            try:
                timebin = my_runs[run][ch]["Sampling"]
            except:
                rprint("[red]\n---Sampling key not found![/red]")
                if check_key(OPT, "TIMEBIN") == True:
                    timebin = OPT["TIMEBIN"]

            X = timebin * np.arange(len(signal))

            # Define noise (should be imported in future iterations)
            noise_amp = 0.5
            if check_key(OPT, "NOISE_AMP") == True:
                noise_amp = OPT["NOISE_AMP"]
            if noise_run == []:
                noise = np.random.normal(
                    0, noise_amp * np.max(template), size=len(signal)
                )
                fft_noise = np.fft.rfft(noise)
            else:
                fft_noise, fft_noise_X = compute_power_spec(noise_run, timebin)

            # Calculate fft arrays
            fft_signal = np.fft.rfft(signal)
            fft_signal_X = np.fft.rfftfreq(len(signal), my_runs[run][ch]["Sampling"])

            i_template, f_template = find_baseline_cuts(template)
            # conv_template = np.convolve(template, )
            fft_template = np.fft.rfft(template)
            wiener = abs(fft_template) ** 2 / (
                abs(fft_template) ** 2 + abs(fft_noise) ** 2
            )

            if (
                check_key(OPT, "NORM_DET_RESPONSE") == True
                and OPT["NORM_DET_RESPONSE"] == True
            ):
                fft_template = fft_template / np.max(fft_template)
            fft_template_X = np.fft.rfftfreq(len(template), timebin)

            if check_key(OPT, "FILTER") == True and OPT["FILTER"] == "WIENER":
                fft_filter_signal = fft_signal * wiener
                filter_signal = np.fft.irfft(fft_filter_signal)
                label = "Wiener"

                # Generate deconvoluted function
                fft_dec = fft_filter_signal / np.array(fft_template)

            else:
                # Interpolate wiener envelop for fit of gaussian filter
                wiener_buffer = 800
                if check_key(OPT, "WIENER_BUFFER") == True:
                    wiener_buffer = OPT["WIENER_BUFFER"]
                wiener_curve = Curve(
                    fft_template_X[:-wiener_buffer], (-1 * wiener[:-wiener_buffer]) + 2
                )
                env = wiener_curve.envelope2(tc=1e6)
                env_wiener = scipy.interpolate.interp1d(env.x, env.y)
                env_wiener_Y = env_wiener(fft_signal_X[:-wiener_buffer])
                env_wiener_min = np.argmin(-1 * (env_wiener_Y - 2))

                # Select fit parameters and perform fit to determin cut-off
                if check_key(OPT, "FIXED_CUTOFF") == True and OPT["FIXED_CUTOFF"]:
                    params = [my_runs[run][ch]["GaussCutOff"], 2]

                else:
                    try:
                        if (
                            check_key(OPT, "FREE_EXP") == False
                            or OPT["FREE_EXP"] == False
                        ):
                            p0 = 200
                            lim = [10, 2000]
                            popt, cov = curve_fit(
                                lambda f, fc: fit_dec_gauss(f, fc, 2),
                                np.arange(len(fft_signal_X))[:env_wiener_min],
                                np.log10(-1 * (env_wiener_Y[:env_wiener_min] - 2)),
                                p0=p0,
                                bounds=lim,
                            )
                            perr = np.sqrt(np.diag(cov))
                            params = [popt, 2]
                            rprint(
                                "\n-------------- GAUSS FILTER FIT VALUES --------------"
                            )
                            rprint(
                                "%s:\t%.2E\t%.2E"
                                % ("CUT-OFF FREQUENCY", popt[0], perr[0])
                            )
                            rprint(
                                "-----------------------------------------------------\n"
                            )

                            my_runs[run][ch]["GaussCutOff"] = popt[0]

                        elif (
                            check_key(OPT, "FREE_EXP") == True
                            and OPT["FREE_EXP"] == True
                        ):
                            p0 = [50, 2]
                            lim = [[10, 1], [500, 8]]
                            params, cov = curve_fit(
                                fit_dec_gauss,
                                np.arange(len(fft_signal_X))[:env_wiener_min],
                                np.log10(-1 * (env_wiener_Y[:env_wiener_min] - 2)),
                                p0=p0,
                                bounds=lim,
                            )

                    except:
                        params = [50, 2]
                        rprint("[red]FIT COULD NOT BE PERFORMED![/red]")
                        rprint("Filter strengh %f and exp %f" % (params[0], params[1]))

                # Generate gauss filter and filtered signal
                fft_gauss = dec_gauss(np.arange(len(fft_signal)), *params)
                fft_gauss[0] = 0
                # if check_key(OPT,  "PRO_RODRIGO") ==  True and OPT["PRO_RODRIGO"] ==  True:

                fft_filter_signal = fft_signal * fft_gauss
                filter_signal = np.fft.irfft(fft_filter_signal)
                label = "Gauss"

                # Generate deconvoluted function
                fft_dec = fft_filter_signal / np.array(fft_template)

            dec = np.fft.irfft(fft_dec)
            # dec = np.roll(dec, np.argmax(template)) # Roll the function to match original position

            dec_std = np.mean(dec[: np.argmax(dec) - peak_buffer])
            dec = dec - dec_std

            i_signal, f_signal = find_baseline_cuts(signal)
            i_resp, f_resp = find_baseline_cuts(template)
            i_dec, f_dec = find_baseline_cuts(dec)
            dec_baseline_charge = np.trapz(
                dec[i_signal:f_signal],
                my_runs[run][ch]["Sampling"] * np.arange(len(dec[i_signal:f_signal])),
            )
            dec_charge = np.trapz(
                dec, my_runs[run][ch]["Sampling"] * np.arange(len(dec))
            )

            if check_key(OPT, "CONVERT_ADC") == True and OPT["CONVERT_ADC"] == True:
                # dec = dec*np.sum(abs(fft_signal))/np.sum(abs(fft_dec))
                dec = dec * np.max(abs(fft_signal)) / np.max(abs(fft_dec))
                dec_baseline_charge = np.trapz(
                    dec[i_signal:f_signal],
                    my_runs[run][ch]["Sampling"]
                    * np.arange(len(dec[i_signal:f_signal])),
                )
                dec_charge = np.trapz(
                    dec, my_runs[run][ch]["Sampling"] * np.arange(len(dec))
                )
                if (
                    check_key(OPT, "TERMINAL_OUTPUT") == True
                    and OPT["TERMINAL_OUTPUT"] == True
                ):
                    rprint(
                        "\nDECONVOLUTION: baseline int  = \t %.2E" % dec_baseline_charge
                    )
                if (
                    check_key(OPT, "TERMINAL_OUTPUT") == True
                    and OPT["TERMINAL_OUTPUT"] == True
                ):
                    rprint("DECONVOLUTION: total int  = \t %.2E\n" % dec_charge)
                # rprint("Converting dec wvf amp to ADC")

            aux.append(dec)

            # -------------------------------------------------------------------------------------------------------------------
            # Plot results: left shows process in time space; right in frequency space.
            # -------------------------------------------------------------------------------------------------------------------
            if check_key(OPT, "SHOW") == True and OPT["SHOW"] == True:
                plt.ion()
                next_plot = False
                fig = plt.figure()
                plt.rcParams["figure.figsize"] = [16, 8]
                plt.subplot(1, 2, 1)
                plt.title("DECONVOLUTION RUN %s CH %s" % (run, ch))

                if check_key(OPT, "NORM") == True and OPT["NORM"] == True:
                    plt.plot(
                        X,
                        signal / np.max(signal),
                        label="SIGNAL: int = %.4E"
                        % (np.trapz(signal[i_signal:f_signal], X[i_signal:f_signal])),
                        c="tab:blue",
                        ds="steps",
                    )
                    if check_key(OPT, "SHOW_GAUSS_SIGNAL") != False:
                        plt.plot(
                            X,
                            filter_signal / np.max(filter_signal),
                            label="GAUSS_SIGNAL: int = %.4E"
                            % (
                                np.trapz(
                                    filter_signal[i_signal:f_signal],
                                    X[i_signal:f_signal],
                                )
                            ),
                            c="blue",
                        )
                    plt.plot(
                        X,
                        template / np.max(template),
                        label="DET_RESPONSE: int = %.4E"
                        % (np.trapz(template[i_resp:f_resp], X[i_resp:f_resp])),
                        c="tab:orange",
                        ds="steps",
                    )
                    if (
                        check_key(OPT, "CONVERT_ADC") == True
                        and OPT["CONVERT_ADC"] == True
                    ):
                        plt.plot(
                            X,
                            dec,
                            label="DECONVOLUTION: int = %.2E" % dec_baseline_charge,
                            c="tab:red",
                            ds="steps",
                            lw=2.0,
                        )
                    else:
                        plt.plot(
                            X,
                            dec,
                            label="DECONVOLUTION: int = %.2f PE"
                            % (np.sum(dec[i_dec:f_dec])),
                            c="tab:red",
                            ds="steps",
                            lw=2.0,
                        )
                else:
                    plt.plot(
                        X,
                        signal,
                        label="SIGNAL: int = %.4E"
                        % (np.trapz(signal[i_signal:f_signal], X[i_signal:f_signal])),
                        c="tab:blue",
                        ds="steps",
                    )
                    if check_key(OPT, "SHOW_GAUSS_SIGNAL") != False:
                        plt.plot(
                            X,
                            filter_signal,
                            label="GAUSS_SIGNAL: int = %.4E"
                            % (
                                np.trapz(
                                    filter_signal[i_signal:f_signal],
                                    X[i_signal:f_signal],
                                )
                            ),
                            c="blue",
                        )
                    plt.plot(
                        X,
                        template,
                        label="DET_RESPONSE: int = %.4E"
                        % (np.trapz(template[i_resp:f_resp], X[i_resp:f_resp])),
                        c="tab:orange",
                        ds="steps",
                    )
                    if (
                        check_key(OPT, "CONVERT_ADC") == True
                        and OPT["CONVERT_ADC"] == True
                    ):
                        plt.plot(
                            X,
                            dec,
                            label="DECONVOLUTION: int = %.2E" % dec_baseline_charge,
                            c="tab:red",
                            ds="steps",
                            lw=2.0,
                        )
                    else:
                        plt.plot(
                            X,
                            dec,
                            label="DECONVOLUTION: int = %.2f PE"
                            % (np.sum(dec[i_dec:f_dec])),
                            c="tab:red",
                            ds="steps",
                            lw=2.0,
                        )

                # plt.axhline(0, label = "Total # PE in deconvolved signal %f"%np.sum(dec), c = "black", alpha = 0.5, ls = "--")
                if (
                    check_key(OPT, "CONVERT_ADC") == False
                    or OPT["CONVERT_ADC"] == False
                ):
                    if (
                        check_key(OPT, "TERMINAL_OUTPUT") == True
                        and OPT["TERMINAL_OUTPUT"] == True
                    ):
                        rprint(
                            "\nDECONVOLUTION: baseline int  = \t %.2f PE"
                            % (np.sum(dec[i_dec:f_dec]))
                        )
                    if (
                        check_key(OPT, "TERMINAL_OUTPUT") == True
                        and OPT["TERMINAL_OUTPUT"] == True
                    ):
                        rprint("DECONVOLUTION: total int  = \t %.2f PE\n" % np.sum(dec))
                plt.axhline(0, c="black", alpha=0.5, ls="--")
                # rprint("# PE in deconvolved signal %f"%np.sum(dec[i_dec:f_dec]))

                plt.ylabel("ADC Counts")
                plt.xlabel("Time in [s]")
                if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
                    if check_key(OPT, "THRLD") == True:
                        thrld = OPT["THRLD"]
                    else:
                        thrld = 1e-6
                    plt.semilogy()
                    plt.ylim(thrld)
                if check_key(OPT, "FOCUS") == True and OPT["FOCUS"] == True:
                    plt.xlim(
                        4e-9
                        * np.array([np.argmax(signal) - 100, np.argmax(signal) + 1000])
                    )
                    plt.ylim([np.min(signal) * 1.1, np.max(dec) * 1.1])
                plt.legend()

                plt.subplot(1, 2, 2)
                if check_key(OPT, "SHOW_F_SIGNAL") != False:
                    plt.plot(
                        fft_signal_X, np.abs(fft_signal), label="SIGNAL", c="tab:blue"
                    )
                if check_key(OPT, "SHOW_F_GSIGNAL") != False:
                    plt.plot(
                        fft_signal_X,
                        np.abs(fft_filter_signal),
                        label="GAUSS_SIGNAL",
                        c="blue",
                    )
                if check_key(OPT, "SHOW_F_DET_RESPONSE") != False:
                    plt.plot(
                        fft_template_X,
                        np.abs(fft_template),
                        label="DET_RESPONSE",
                        c="tab:orange",
                    )
                plt.axhline(1, ls="--", c="grey")
                if check_key(OPT, "SHOW_F_DEC") != False:
                    plt.plot(
                        fft_signal_X,
                        np.abs(fft_dec),
                        label="DECONVOLUTION",
                        c="tab:red",
                    )
                if check_key(OPT, "SHOW_F_WIENER") != False:
                    plt.plot(
                        fft_signal_X, wiener, label="WIENER", c="tab:orange", ls="--"
                    )
                    # plt.plot(env_wiener.x[:env_wiener_min], -1*(env_wiener.y[:env_wiener_min]-2), label = "ENV_WIENER", c = "tab:pink", ls = "--")

                if check_key(OPT, "SHOW_F_GAUSS") != False:
                    if OPT["SHOW_F_GAUSS"] == True:
                        plt.plot(fft_signal_X, fft_gauss, label="GAUSS", c="tab:green")
                
                plt.ylabel("a.u.")
                plt.xlabel("Frequency in [Hz]")
                plt.ylim(1e-8, np.max(fft_signal) * 100)
                plt.semilogy()
                plt.semilogx()
                plt.legend()

                while not plt.waitforbuttonpress(-1):
                    pass
                if check_key(OPT, "SAVE") == True and OPT["SAVE"] == True:
                    save_figure(fig, f"{info['OUT_PATH'][0]}/images/", run, ch, "Deconvolution", debug=debug)
                    # plt.savefig(
                    #     f"{info['OUT_PATH'][0]}/images/run{run}/ch{ch}/run{run}_ch{ch}_Deconvolution.png",
                    #     dpi=500,
                    # )
                plt.clf()

        plt.ioff()
        my_runs[run][ch][label + keys[2]] = np.asarray(aux)
        if check_key(OPT, "CONVERT_ADC") == True and OPT["CONVERT_ADC"] == True:
            my_runs[run][ch][label + keys[2] + "ADC"] = np.asarray(aux)
        rprint("Generated wvfs with key %s" % (label + keys[2]))
    plt.close()


# def convolve(my_runs, keys = [], OPT = {}):

#     rprint("\n### WELCOME TO THE CONVOLUTION STUDIES ###\n", "blue", bold=True)
#     for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
#         aux = dict()

#         for i in range(len(my_runs[run][ch][keys[0]])):
#             # Select required runs and parameters

#             signal = my_runs[run][ch][keys[0]][i]

#             timebin = my_runs[run][ch]["Sampling"]
#             if check_key(OPT, "TIMEBIN") ==  True: timebin = OPT["TIMEBIN"]
#             X = timebin*np.arange(len(signal))

#             ########################################################################
#             #_____________________CONVOLUTION_AND_FIT_PARAMETERS___________________#
#             ########################################################################

#             # MUON SC CONFIG
#             t_fast   = 2e-8; t_fast_low   = 1e-8; t_fast_high   = 4e-8
#             t_slow   = 1e-6; t_slow_low   = 6e-7; t_slow_high   = 5e-6
#             amp_fast = 2e-8; amp_fast_low = 1e-8; amp_fast_high = 3e-8
#             amp_slow = 5e-8; amp_slow_low = 1e-8; amp_slow_high = 9e-8
#             sigma    = 2e-8; sigma_low    = 9e-9; sigma_high    = 3e-8

#             # MUON SiPM CONFIG
#             t_fast   = 2e-8; t_fast_low   = 1e-8; t_fast_high   = 4e-8
#             t_slow   = 1.2e-6; t_slow_low = 1e-6; t_slow_high   = 5e-6
#             amp_fast = 2e-8; amp_fast_low = 1e-8; amp_fast_high = 3e-8
#             amp_slow = 2e-8; amp_slow_low = 8e-9; amp_slow_high = 9e-8
#             sigma    = 2e-8; sigma_low    = 9e-9; sigma_high    = 3e-8

#             fit_initials = (t_fast, t_slow, amp_fast, amp_slow, sigma)
#             fit_finals   = [t_fast, t_slow, amp_fast, amp_slow, sigma]
#             limits_low   = [t_fast_low, t_slow_low, amp_fast_low, amp_slow_low, sigma_low]
#             limits_high  = [t_fast_high, t_slow_high, amp_fast_high, amp_slow_high, sigma_high]
#             fit_limits   = (limits_low, limits_high)

#             popt,  pcov = curve_fit(conv_func2, [laser.wvf_x[:-limit], laser.wvf[:-limit]], alpha.wvf[:-limit],  p0 = fit_initials,  bounds = fit_limits, method = "trf")
#             perr = np.sqrt(np.diag(pcov))
#             conv = conv_func2([laser.wvf_x[:-limit], laser.wvf[:-limit]], *popt)
#             func = func2(alpha.wvf_x, *popt)
#             conv_int, f_conv, i_conv = signal_int("CONV FUNC", func2(np.arange(0, alpha.wvf_x[-1], 5e-10), *popt), timebin, "SiPM", "ALL", th = thrld, out = True)

#             labels = ["TFAST", "TSLOW", "AFAST", "ASLOW", "SIGMA"]
#             rprint("\n--- FIT VALUES ---")
#             for i in range(len(fit_initials)):
#                 fit_finals[i] = popt[i]
#                 rprint("%s: %.2E \u00B1 %.2E"%(labels[i], popt[i], perr[i]))
#             rprint("------------------\n")

#             rprint("SLOW = %.2f%%"%(100*popt[3]/(popt[3]+popt[2])))

#             ########################################################################
#             #________________________PLOT_FIRST_RESULT_____________________________#
#             ########################################################################

#             # fig1,  axs = plt.subplots(2,  1,  sharex = True)

#             fig1,  axs = plt.subplots(2,  1)
#             plt.title(decon_runs)
#             fig1.subplots_adjust(hspace = 0.25)
#             fig1.set_figheight(6)
#             fig1.set_figwidth(6)

#             # axs[0] = plt.subplot2grid(shape = (1,  1),  loc = (0,  0),  colspan = 3)
#             # axs[1] = plt.subplot2grid(shape = (1,  1),  loc = (3,  0),  colspan = 3)

#             axs[0].plot(laser.wvf_x, laser.wvf, label = label_luz)
#             axs[0].plot(alpha.wvf_x, alpha.wvf, label = label_alp)
#             axs[0].plot(laser.wvf_x[:-limit], conv, label = "Fitted Convolution")
#             axs[0].axvline(laser.wvf_x[-limit], color = "grey",  ls = ":")
#             axs[0].set_ylabel("Normalized Amplitude")
#             axs[0].axhline(0, color = "grey",  ls = ":")
#             axs[0].set_ylim(1e-4, np.max(alpha.wvf)*1.5)
#             axs[0].legend()
#             if logy ==  True:
#                 axs[0].semilogy()
#                 axs[1].semilogy()

#             axs[1].plot(alpha.wvf_x[np.argmax(alpha.wvf)-np.argmax(func):], func[:np.argmax(func)-np.argmax(alpha.wvf)], label = "Convolution Func.")
#             axs[1].axhline(0, color = "grey",  ls = ":")
#             axs[1].set_ylim(1e-6, 10)
#             axs[1].set_xlabel("Time in [s]"); axs[1].set_ylabel("Convolution signal")

#             plt.show()

#             # output_file.write("%.2E \t\u00B1\t %.2E\n"%(p, perr2[0]))
#             # output_file.write("%.2E \t\u00B1\t %.2E\n"%(t0, perr1[4]))
#             output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[4], perr[4]))
#             output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[2], perr[2]))
#             output_file.write("%.2E \t\u00B1\t %.2E\n"%(fit_finals[0], perr[0]))


def check_array_len(wvf1, wvf2):
    if len(wvf1) < len(wvf2):
        rprint("[yellow]RAW WVF IS LONGER THAN WVF TEMPLATE[/yellow]")
        wvf2 = wvf2[: -(len(wvf2) - len(wvf1))]
    if len(wvf1) > len(wvf2):
        rprint("[yellow]RAW WVF IS SHORTER THAN WVF TEMPLATE[/yellow]")
        wvf1 = wvf1[: -(len(wvf1) - len(wvf2))]

    return wvf1, wvf2


def check_array_even(wvf):
    if len(wvf) % 2 > 0:
        return wvf[:-1]
    else:
        return wvf


def conv_func2(wvf, t0, sigma, tau1, a1, tau2, a2):
    resp = func2(wvf[0], 0, t0, sigma, a1, tau1, a2, tau2)

    conv = convolve(wvf[1], resp)
    conv = conv / np.max(conv)
    wvf_max = np.argmax(wvf[1])
    conv_max = np.argmax(conv)

    return conv[conv_max - wvf_max : conv_max + len(wvf[1]) - wvf_max]


def logconv_func2(wvf, t0, sigma, tau1, a1, tau2, a2):
    resp = logfunc2(wvf[0], 0, t0, sigma, a1, tau1, a2, tau2)

    conv = convolve(wvf[1], resp)
    conv = conv / np.max(conv)
    wvf_max = np.argmax(wvf[1])
    conv_max = np.argmax(conv)

    return conv[conv_max - wvf_max : conv_max + len(wvf[1]) - wvf_max]
