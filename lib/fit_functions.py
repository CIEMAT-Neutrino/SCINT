# ================================================================================================================================================#
# This library contains functions to perform fits to the data.                                                                                   #
# ================================================================================================================================================#
from srcs.utils import get_project_root

import os, stat, math, scipy
from lmfit import models
from typing import Optional
from itertools import product
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import numpy as np
from scipy.special import erf

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from math import factorial as fact
from rich import print as rprint
from scipy.ndimage import gaussian_filter1d

# Imports from other libraries
from .io_functions import check_key, read_yaml_file, save_figure
from .ana_functions import find_amp_decrease
from .unit_functions import get_run_units
from .sty_functions import get_prism_colors

np.seterr(divide="ignore")
root = get_project_root()
colors = get_prism_colors()

# ===========================================================================#
# ************************** THEORETICAL FUNCTIONS **************************#
# ===========================================================================#


def chi_squared(x, y, popt):
    fit_y = np.sum(
        [gaussian(x, popt[j], popt[j + 1], popt[j + 2]) for j in range(0, len(popt), 3)]
    )
    return np.sum((y - fit_y) ** 2 / fit_y) / (y.size - len(popt))


def pure_scint(time, t0, a1, a2, tau1, tau2):
    y = a1 / tau1 * np.exp(-(time - t0) / tau1) + a2 / tau2 * np.exp(
        -(time - t0) / tau2
    )


def gauss(x, a, x0, sigma):
    return (
        a
        / (sigma * math.sqrt(2 * math.pi))
        * np.exp(-0.5 * np.power((x - x0) / sigma, 2))
    )


def gaussian_train(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        center = params[i]
        height = params[i + 1]
        width = params[i + 2]
        y = y + gaussian(x, center, height, width)
    return y


def loggaussian_train(x, *params):
    y = gaussian_train(x, *params)
    y[y <= 0] = 1e-1
    return np.log(y)


def gaussian(x, center, height, width):
    return height * np.exp(-0.5 * ((x - center) / width) ** 2)


def test_gaussian(x, center, width):
    return np.exp(-0.5 * ((x - center) / width) ** 2)


# def pmt_spe(x, height, center, width):
#     return height * np.exp(-0.5*((x - center)/width)**2)


def loggaussian(x, center, height, width):
    return np.log10(gaussian(x, center, height, width))


def func(t, t0, sigma, a, tau):
    return (
        (2 * a / tau)
        * np.exp((sigma / (np.sqrt(2) * tau)) ** 2 - (np.array(t) - t0) / tau)
        * (1 - erf((sigma**2 - tau * (np.array(t) - t0)) / (np.sqrt(2) * sigma * tau)))
    )


def func2(t, p, t0, sigma, a1, tau1, sigma2, a2, tau2):
    return p + func(t, t0, sigma, a1, tau1) + func(t, t0, sigma2, a2, tau2)


def logfunc2(t, p, t0, sigma1, a1, tau1, sigma2, a2, tau2):
    return np.log(p + func(t, t0, sigma1, a1, tau1) + func(t, t0, sigma2, a2, tau2))


def logfunc3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return np.log(
        p
        + func(t, t0, sigma, a1, tau1)
        + func(t, t0, sigma, a2, tau2)
        + func(t, t0, sigma, a3, tau3)
    )


def func3(t, p, t0, sigma, a1, tau1, a2, tau2, a3, tau3):
    return (
        p
        + func(t, t0, sigma, a1, tau1)
        + func(t, t0, sigma, a2, tau2)
        + func(t, t0, sigma, a3, tau3)
    )


def scfunc(t, a, b, c, d, e, f):
    return (
        a * np.exp(-(t - c) / b) / np.power(2 * np.pi, 0.5) * np.exp(-(d**2) / (b**2))
    ) * (1 - erf(((c - t) / d + d / b) / np.power(2, 0.5))) + (
        e * np.exp(-(t - c) / f) / np.power(2 * np.pi, 0.5) * np.exp(-(d**2) / (f**2))
    ) * (
        1 - erf(((c - t) / d + d / f) / np.power(2, 0.5))
    )


def dec_gauss(f, fc, n):
    y = np.exp(-0.5 * (f / fc) ** n)
    return y


def fit_dec_gauss(f, fc, n):
    y = np.log10(dec_gauss(f, fc, n))
    y[0] = 0
    return y


def purity(t, p, t0, a1, a3, sigma, quenching):
    tau1 = (1 / 7.1e-9 + quenching) ** -1
    tau3 = (1 / 1.66e-6 + quenching) ** -1
    a1_prime = a1 / (1 + tau1 * quenching)
    a3_prime = a3 / (1 + tau3 * quenching)
    return p + func(t, t0, sigma, a1_prime, tau1) + func(t, t0, sigma, a3_prime, tau3)


def simple_purity(t, p, t0, a0, a1, sigma, quenching):
    tau1 = (1 / 7.1e-9 + quenching) ** -1
    tau3 = (1 / 1.66e-6 + quenching) ** -1
    a1_prime = a0 / (1 + tau1 * quenching)
    a3_prime = (a0 * (1 - a1) / a1) / (1 + tau3 * quenching)
    return p + func(t, t0, sigma, a1_prime, tau1) + func(t, t0, sigma, a3_prime, tau3)


def logpurity(t, p, t0, a1, a3, sigma, quenching):
    return np.log(purity(t, p, t0, a1, a3, sigma, quenching))


def logsimple_purity(t, p, t0, a0, a1, sigma, quenching):
    return np.log(simple_purity(t, p, t0, a0, a1, sigma, quenching))


def lmfit_models(function):
    # if function == "gaussian":    return models.GaussianModel()
    if function == "linear":
        return models.LinearModel()
    if function == "lorentzian":
        return models.LorentzianModel()
    if function == "exponential":
        return models.ExponentialModel()
    if function == "powerlaw":
        return models.PowerLawModel()
    # Lmfit for initial parameters
    # model  = lmfit_models(function)
    # params = model.guess(ydata, x=xdata)
    # result = model.fit  (ydata, params, x=xdata)
    # rprint(f'Chi-square = {result.chisqr:.4f}, Reduced Chi-square = {result.redchi:.4f}')


# --------------------------------------------------------------------------- #
# THIS LIBRARY NEED MIMO PORQUE HAY COSAS REDUNDANTES QUE SE PUEDEN UNIFICAR
def fit_gaussians(x, y, *p0):
    assert x.shape == y.shape, "Input arrays must have the same shape."
    popt, pcov = curve_fit(gaussian_train, x, y, p0=p0[0])
    fit_y = gaussian_train(x, *popt)
    chi_squared = np.sum(
        (y[abs(fit_y) > 0.1] - fit_y[abs(fit_y) > 0.1]) ** 2 / fit_y[abs(fit_y) > 0.1]
    ) / (y.size - len(popt))
    return popt, fit_y, chi_squared


##Binomial+Poisson distribution
def B(i, k, debug=False):
    """
    Factorial factor of F
    """
    if (i == 0) & (k == 0):
        return 1
    if (i == 0) & (k > 0):
        return 0
    else:
        return fact(k - 1) * fact(k) / (fact(i - 1) * fact(i) * fact(k - i))


def F(K, p, L, debug=False):
    """
    Computes prob of the kth point in a convoluted poisson+binomial distribution.
    L is the mean value of the poisson, p is the binomial coef, i.e. the crosstalk we want to compute
    """
    aux_sum = 0
    if debug:
        rprint(K)
    for i in range(K + 1):
        aux_sum += B(i, K) * ((L * (1 - p)) ** i) * (p ** (K - i))
    return np.exp(-L) * aux_sum / fact(K)


def PoissonPlusBinomial(x, N, p, L, debug=False):
    # N   = len(x)
    N = int(N)
    aux = np.zeros(shape=N)
    for i in range(N):
        if debug:
            rprint(x, i, x[i])
        aux[i] = F(int(x[i]), p, L)
    return aux / sum(aux)


# ===========================================================================#
# *********************** FITTING FUNCTIONS *********************************#
# ===========================================================================#
def gaussian_fit(counts, bins, bars, thresh, fit_function="gaussian", custom_fit=[0]):
    """This function fits the histogram, to a gaussians.
    
    :params counts: counts of the histogram
    :type counts: np.array
    :params bins: bins of the histogram
    :type bins: np.array
    :params bars: bars of the histogram
    :type bars: np.array
    :params thresh: threshold value (for height of peaks and valleys)
    :type thresh: int
    :params fit_function: function to fit to, defaults to "gaussian"
    :type fit_function: str, optional
    :params custom_fit: custom fit, defaults to [0]
    :type custom_fit: list, optional
    
    :return: x, popt, pcov, perr -- x values, fit parameters, covariance matrix and errors
    :rtype: tuple
    """

    #### PEAK FINDER PARAMETERS #### thresh = int(len(my_runs[run][ch][key])/1000), wdth = 10 and prom = 0.5 work well
    wdth = 10
    prom = 0.5
    acc = 1000

    ## Create linear interpolation between bins to search peaks in these variables ##
    if len(custom_fit) == 2:
        mean = custom_fit[0]
        sigma = custom_fit[1]

        x = np.linspace(mean - sigma, mean + sigma, acc)
        y_intrp = scipy.interpolate.interp1d(bins[:-1], counts)
        y = y_intrp(x)
    else:
        x = np.linspace(bins[1], bins[-2], acc)
        y_intrp = scipy.interpolate.interp1d(bins[:-1], counts)
        y = y_intrp(x)

    rprint("\n...Fitting to a gaussian...")
    ## Find indices of peaks ##
    if fit_function == "gaussian":
        peak_idx, _ = find_peaks(y, height=thresh, width=wdth, prominence=prom)
    if fit_function == "loggaussian":
        peak_idx, _ = find_peaks(
            np.log10(y), height=np.log10(thresh), width=wdth, prominence=prom
        )

    if len(custom_fit) == 2:
        rprint("\n--- Customized fit ---")
        mean = float(custom_fit[0])
        sigma = float(custom_fit[1])
        best_peak_idx = peak_idx[np.abs(x[peak_idx] - mean).argmin()]
        best_peak_idx1 = best_peak_idx + 50

        x_gauss = x
        y_gauss = y
        rprint("Taking peak at: ", x[best_peak_idx])
    else:
        sigma = abs(wdth * (bins[0] - bins[1]))
        best_peak_idx = peak_idx[0]
        best_peak_idx1 = best_peak_idx + 50

        x_space = np.linspace(
            x[best_peak_idx] - sigma, x[best_peak_idx1] + sigma, acc
        )  # Array with values between the x_coord of 2 consecutives peaks
        step = x_space[1] - x_space[0]
        x_gauss = x_space - int(acc / 2) * step
        x_gauss = x_gauss[x_gauss >= bins[0]]
        y_gauss = y_intrp(x_gauss)
        rprint("Taking peak at: ", x[best_peak_idx])

    # try:
    popt, pcov = curve_fit(
        gaussian,
        x_gauss,
        y_gauss,
        p0=[x[best_peak_idx1], y[best_peak_idx], sigma],
        maxfev=5000,
    )
    # popt, pcov = curve_fit(gaussian,x_gauss,y_gauss,p0=[y[best_peak_idx],x[best_peak_idx1]],sigma = sigma, absolute_sigma=True, maxfev=5000)
    perr = np.sqrt(np.diag(pcov))
    chi2 = chi_squared(x_gauss, y_gauss, popt)
    # except:
    #     rprint("WARNING: Peak could not be fitted")

    return x, popt, pcov, perr
    # return x, popt, pcov, perr, chi2 # UPLOAD WHEN POSSIBLE MERGING IN MAIN BRANCH; upgrade all the fit functions


def peak_valley_finder(x, y, params):
    """This function finds the alternating peaks and valleys of the histogram.
    """
    
    dist = params["PEAK_DISTANCE"]
    thresh = params["THRESHOLD"]
    wdth = params["WIDTH"]
    prom = params["PROMINENCE"]
    acc = params["ACCURACY"]
    max_y = np.max(y)
    y_norm = y / max_y

    # Initial peak and valley detection
    peak_idx, _ = find_peaks(y_norm, height=thresh, width=wdth, prominence=prom, distance=dist)
    valley_idx, _ = find_peaks(1 - y_norm, height=0, width=wdth, prominence=prom, distance=dist)

    # Combine and sort
    points = [(p, 'peak') for p in peak_idx] + [(v, 'valley') for v in valley_idx]
    points.sort()

    filtered_points = []
    i = 0
    while i < len(points):
        group = [points[i]]
        j = i + 1

        # Group consecutive points of same type (peak or valley)
        while j < len(points) and points[j][1] == points[i][1]:
            group.append(points[j])
            j += 1

        if len(group) == 1:
            filtered_points.append(group[0])
        else:
            # Looking for previous and next points of opposite types
            prev_boundary = points[i - 1][0] if i > 0 else group[0][0] - dist
            next_boundary = points[j][0] if j < len(points) else group[-1][0] + dist

            # Keep the most centered point between the grouped points
            center = (prev_boundary + next_boundary) / 2
            best_point = min(group, key=lambda pt: abs(pt[0] - center))
            filtered_points.append(best_point)

        i = j

    # Separate indices by type
    final_peaks = np.array([i for i, t in filtered_points if t == 'peak'])
    final_valleys = np.array([i for i, t in filtered_points if t == 'valley'])

    rprint("Peaks found at: ", final_peaks)
    rprint("Valleys found at: ", final_valleys)

    rprint(
        "[cyan]PeakFinder using parameters: dist = %i, thresh = %.2f, wdth = %i, prom = %.2f, acc = %i[/cyan]"
        % (dist, thresh, wdth, prom, acc)
    )
    return final_peaks, final_valleys


def gaussian_train_fit(fig, x, y, y_intrp, peak_idx, valley_idx, params, debug=False):
    """This function fits the histogram, to a train of gaussians.
    """

    initial = []  # Saving for input to the TRAIN FIT
    if len(peak_idx) < len(valley_idx):
        n_peaks = len(peak_idx)  # Number of peaks found by find_peak
    else:
        n_peaks = len(valley_idx)

    labels = [""] * (n_peaks - 1) + ["Initial fit"]
    for i in range(n_peaks):
        if i == 0:
            x_gauss = np.linspace(
                x[peak_idx[i]] - (x[valley_idx[i]] - x[peak_idx[i]]),
                x[valley_idx[i]],
                params["ACCURACY"],
            )  # Array with values between the x_coord of 2 consecutives peaks
        else:
            x_gauss = np.linspace(
                x[valley_idx[i - 1]], x[valley_idx[i]], params["ACCURACY"]
            )

        x_gauss = x_gauss[x_gauss >= x[0]]
        y_gauss = y_intrp(x_gauss)
        # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.9)

        try:
            # (y[peak_idx[i]]),x[peak_idx[i]],abs(wdth*(bins[0]-bins[1]))])
            popt, pcov = curve_fit(
                gaussian,
                x_gauss,
                y_gauss,
                p0=[
                    x[peak_idx[i]],
                    y[peak_idx[i]],
                    abs(params["WIDTH"] * (x_gauss[0] - x_gauss[1])),
                ],
                bounds=(
                    [x[peak_idx[i]] - params["WIDTH"], 0, 0],
                    [
                        x[peak_idx[i]] + params["WIDTH"],
                        np.inf,
                        10 * abs(params["WIDTH"] * (x_gauss[0] - x_gauss[1])),
                    ],
                ),
            )
            perr = np.sqrt(np.diag(pcov))
            ## FITTED to gaussian(x, height, center, width) ##
            initial.append(popt[0])  # CENTER
            initial.append(popt[1])  # HEIGHT
            initial.append(np.abs(popt[2]))  # WIDTH
            # fig.plot(
            #     x_gauss,
            #     gaussian(x_gauss, *popt),
            #     ls="--",
            #     c="black",
            #     alpha=0.5,
            #     label=labels[i],
            # )
        except:
            continue

    pcov = np.zeros((len(initial), len(initial)))
    perr = np.zeros(len(initial))
    popt = initial
    ## GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
    try:
        popt, pcov = curve_fit(
            gaussian_train, x[: valley_idx[-1]], y[: valley_idx[-1]], p0=initial
        )
        perr = np.sqrt(np.diag(pcov))
    except ValueError:
        rprint("[red]Full fit could not be performed[/red]")
    except RuntimeError:
        rprint("[red]Full fit could not be performed[/red]")
    return popt, pcov


def pmt_spe_fit(counts, bins, bars, thresh):
    """This function fits the histogram, to a train of gaussians
    \n[es muy parecida a gaussian_train_fit; hay algunas cosas que las coge en log pero igual se pueden unificar]
    \n[se le puede dedicar un poco mas de tiempo para tener un ajuste mas fino pero parece que funciona]
    """

    ## Threshold value (for height of peaks and valleys) ##
    # thresh = int(len(my_runs[run][ch][key])/1000)
    wdth = 10
    prom = 0.5
    acc = 1000

    ## Create linear interpolation between bins to search peaks in these variables ##
    x = np.linspace(bins[1], bins[-2], acc)
    y_intrp = scipy.interpolate.interp1d(bins[:-1], counts)
    y = y_intrp(x)

    ## Find indices of peaks ##
    peak_idx, _ = find_peaks(
        np.log(y), height=np.log(thresh), width=wdth, prominence=prom
    )
    # peak_idx, _ = find_peaks(y, height = thresh, width = wdth, prominence = prom)
    ## Find indices of valleys (from inverting the signal) ##
    valley_idx, _ = find_peaks(
        -np.log(y),
        height=[-np.max(np.log(counts)), -np.log(thresh)],
        width=wdth,
        prominence=prom,
    )
    # valley_idx, _ = find_peaks(-y, height = [-np.max(counts), -thresh], width = wdth)

    n_peaks = 4  # Fit of ped+1pe+2pe
    initial = []  # Saving for input to the TRAIN FIT
    if len(peak_idx) - 1 < n_peaks:
        n_peaks = len(peak_idx) - 1  # Number of peaks found by find_peak

    for i in range(n_peaks):
        x_space = np.linspace(
            x[peak_idx[i]], x[peak_idx[i + 1]], acc
        )  # Array with values between the x_coord of 2 consecutives peaks
        step = x_space[1] - x_space[0]
        x_gauss = x_space - int(acc / 2) * step
        x_gauss = x_gauss[x_gauss >= bins[0]]
        y_gauss = y_intrp(x_gauss)
        # plt.plot(x_gauss,y_gauss,ls="--",alpha=0.9)

        try:
            popt, pcov = curve_fit(
                gaussian,
                x_gauss,
                y_gauss,
                p0=[y[peak_idx[i]], x[peak_idx[i]], abs(wdth * (bins[0] - bins[1]))],
            )
            perr = np.sqrt(np.diag(pcov))
            ## FITTED to gaussian(x, height, center, width) ##
            initial.append(popt[1])  # HEIGHT
            initial.append(popt[0])  # CENTER
            initial.append(np.abs(popt[2]))  # WIDTH
            # plt.plot(x_gauss,gaussian(x_gauss, *popt), ls = "--", c = "black", alpha = 0.5)
            # plt.ylim((1e-2,1e5))
        except:
            initial.append(x[peak_idx[i]])
            initial.append(y[peak_idx[i]])
            initial.append(abs(wdth * (bins[0] - bins[1])))
            rprint("[red]Peak %i could not be fitted[/red]" % i)

    try:
        # GAUSSIAN TRAIN FIT ## Taking as input parameters the individual gaussian fits with initial
        # popt, pcov = curve_fit(loggaussian_train,x[:peak_idx[-1]],np.log10(y[:peak_idx[-1]]),p0=initial)
        popt, pcov = curve_fit(
            gaussian_train, x[: peak_idx[-1]], y[: peak_idx[-1]], p0=initial
        )
        perr = np.sqrt(np.diag(pcov))
    except:
        popt = initial
        rprint("[red]Full fit could not be performed[/red]")

    return x, y, peak_idx, valley_idx, popt, pcov, perr


def cut_threshold(raw, thld):
    for i in range(len(raw)):
        if raw[i] <= thld:
            raw[i] = thld
        if np.isnan(raw[i]):
            raw[i] = thld
        if np.isinf(raw[i]):
            raw[i] = thld
    return raw


def peak_fit(
    fit_raw, raw_x, buffer, thld, sigma_fast=1e-9, a_fast=1, tau_fast=1e-8, OPT={}
):
    """This function fits the peak to a gaussian function, and returns the parameters
    """

    raw_max = np.argmax(fit_raw)
    if check_key(OPT, "CUT_THRESHOLD") == True and OPT["CUT_THRESHOLD"] == True:
        fit_raw = cut_threshold(fit_raw, thld)

    guess_t0 = raw_x[raw_max]
    p = np.mean(fit_raw[: raw_max - buffer])

    t0 = guess_t0
    t0_low = guess_t0 * 0.02
    t0_high = guess_t0 * 50

    sigma = sigma_fast
    sigma_low = sigma * 1e-2
    sigma_high = sigma * 1e2
    a1 = a_fast
    a1_low = a_fast * 1e-2
    a1_high = a_fast * 1e2
    tau1 = tau_fast
    tau1_low = 6e-9
    tau1_high = tau1 * 1e2

    bounds = (
        [t0_low, sigma_low, a1_low, tau1_low],
        [t0_high, sigma_high, a1_high, tau1_high],
    )
    initial = [t0, sigma, a1, tau1]
    labels = ["TIME", "SIGM", "AMP1", "TAU1"]

    # FIT PEAK
    # try:
    popt, pcov = curve_fit(
        func,
        raw_x[raw_max - buffer : raw_max + int(buffer / 2)],
        fit_raw[raw_max - buffer : raw_max + int(buffer / 2)],
        p0=initial,
    )
    perr = np.sqrt(np.diag(pcov))
    # except:
    # rprint("Peak fit could not be performed")
    # popt = initial
    # perr = np.zeros(len(initial))

    # PRINT FIRST FIT VALUE
    if check_key(OPT, "TERMINAL_OUTPUT") == True and OPT["TERMINAL_OUTPUT"] == True:
        rprint("\n--- FISRT FIT VALUES (FAST) ---")
        for i in range(len(initial)):
            rprint("%s:\t%.2E\t%.2E" % (labels[i], popt[i], perr[i]))
        rprint("-------------------------------")

    # EXPORT FIT PARAMETERS
    # a1 = popt[2];sigma = popt[1];tau1 = popt[3];t0 = popt[0]

    return popt, perr


def sipm_fit(info, labels, raw, raw_x, fit_range, thld=1e-6, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """

    run, ch, key = labels
    max_x = np.argmax(raw)
    # thld = 1e-4
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    OPT["CUT_THRESHOLD"] = True
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thld=thld, OPT=OPT)

    p = np.mean(raw[: max_x - buffer1])
    a1 = 2e-5
    a1_low = 1e-8
    a1_high = 9e-2
    a2 = 2e-5
    a2_low = 1e-8
    a2_high = 9e-2
    a3 = 2e-5
    a3_low = 1e-8
    a3_high = 9e-2
    tau1 = 9e-8
    tau1_low = 6e-9
    tau1_high = 1e-7
    tau2 = 9e-7
    tau2_low = tau1_high
    tau2_high = 1e-6
    tau3 = 9e-6
    tau3_low = tau2_high
    tau3_high = 1e-5
    sigma2 = popt1[1] * 10
    sigma2_low = popt1[1]
    sigma2_high = popt1[1] * 100

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    bounds2 = (
        [sigma2_low, a2_low, tau2_low, a3_low, tau3_low],
        [sigma2_high, a2_high, tau2_high, a3_high, tau3_high],
    )
    initial2 = (sigma2, a2, tau2, a3, tau3)
    labels2 = ["SIGM", "AMP2", "TAU2", "AMP3", "TAU3"]
    popt, pcov = curve_fit(
        lambda t, sigma2, a2, tau2, a3, tau3: logfunc3(
            t, p, popt1[0], sigma2, popt1[2], popt1[3], a2, tau2, a3, tau3
        ),
        raw_x[max_x - buffer1 : max_x + buffer2],
        np.log(raw[max_x - buffer1 : max_x + buffer2]),
        p0=initial2,
        bounds=bounds2,
        method="trf",
    )
    perr2 = np.sqrt(np.diag(pcov))

    sigma2 = popt[0]
    a2 = popt[1]
    tau2 = popt[2]
    a3 = popt[3]
    tau3 = popt[4]
    param = [p, a1, sigma2, tau1, popt1[3], a2, tau2, a3, tau3]

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        show_fit(raw, raw_x, func3, raw_max=max_x, buffer1=buffer1, buffer2=buffer2, param=param, OPT=OPT, save=save, debug=debug)

    aux = func3(raw_x, *param)
    return aux, raw, param, perr2, labels2


def scint_fit(info, labels, raw, raw_x, fit_range, thld=1e-6, i_param={}, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """

    run, ch, key = labels
    next_plot = False
    OPT["CUT_THRESHOLD"] = True

    # Define input parameters from dictionary
    sigma = i_param["sigma"]
    a_fast = i_param["a_fast"]
    tau_fast = i_param["tau_fast"]
    a_slow = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]

    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]
    popt1, perr1 = peak_fit(raw, raw_x, buffer1, thld, sigma, a_fast, tau_fast, OPT)

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    p = np.mean(raw[: raw_max - buffer1])
    p_std = np.std(raw[: raw_max - buffer1])

    sigma1 = popt1[1]
    sigma1_low = sigma1 * 0.9
    sigma1_high = sigma1 * 1.1
    a1 = popt1[2]
    a1_low = a1 * 0.9
    a1_high = a1 * 1.1
    tau1 = popt1[3]
    tau1_low = tau1 * 0.9
    tau1_high = tau1 * 1.1

    sigma2 = sigma
    sigma2_low = sigma * 0.9
    sigma2_high = sigma * 1.1
    a2 = a_slow
    a2_low = a_slow * 1e-2
    a2_high = a_slow * 1e2
    tau2 = tau_slow
    tau2_low = tau_slow * 1e-2
    tau2_high = tau_slow * 1e2

    initial2 = (a1, sigma2, a2, tau2)
    # bounds2  = ([a1_low, sigma2_low, a2_low, tau2_low], [a1_high, sigma2_high, a2_high, tau2_high])
    # labels2  = ["AMP1", "SIG2", "AMP2", "TAU2"]

    try:
        popt2, pcov2 = curve_fit(
            lambda t, a1, sigma2, a2, tau2: logfunc2(
                t, p, popt1[0], popt1[1], a1, popt1[3], sigma2, a2, tau2
            ),
            raw_x[raw_max - buffer1 : raw_max + buffer2],
            np.log(raw[raw_max - buffer1 : raw_max + buffer2]),
            p0=initial2,
        )
        perr2 = np.sqrt(np.diag(pcov2))

    except:
        rprint("[red]Fit could not be performed[/red]")
        popt2 = initial2
        perr2 = np.zeros(len(popt2))

    t0 = popt1[0]
    a1 = popt2[0]
    sigma2 = popt2[1]
    a2 = popt2[2]
    tau2 = popt2[3]

    labels = ["PED", "T0", "SIG1", "AMP1", "TAU1", "SIG2", "AMP2", "TAU2"]
    param = [p, popt1[0], popt1[1], popt2[0], popt1[2], popt2[1], popt2[2], popt2[3]]
    perr = [p_std, perr1[0], perr1[1], perr2[0], perr1[2], perr2[1], perr2[2], perr2[3]]

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        show_fit(info, raw, raw_x, func2, (run, ch, key), raw_max=raw_max, buffer1=buffer1, buffer2=buffer2, param=param, OPT=OPT, save=save, debug=debug)

    aux = func2(raw_x, *param)
    return aux, raw, param, perr, labels


def purity_fit(info, labels, raw, raw_x, fit_range, thld=1e-6, i_param={}, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """

    run, ch, key = labels
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    initial = []
    labels = ["PED", "T0", "A1", "A3", "SIGMA", "QUENCH"]
    for init in labels:
        if init not in i_param:
            if init == "PED":
                initial.append(np.mean(raw[: raw_max - buffer1]))
            if init == "T0":
                initial.append(raw_x[raw_max])
        else:
            initial.append(i_param[init])

    # if np.any(np.isnan(raw)) or np.any(np.isinf(raw)) or np.any(raw <= 0):
    #     rprint("[red]Negative/Infinite/Zero/Nan values found in raw[/red]")

    if check_key(OPT, "FILTER") and isinstance(OPT["FILTER"], int):
        rprint(
            "Filtering the signal with a gaussian filter of sigma = %i" % OPT["FILTER"]
        )
        raw = gaussian_filter1d(raw, sigma=OPT["FILTER"])

    if check_key(OPT, "LOG") and OPT["LOG"]:
        func = logpurity
        if check_key(OPT, "CUT_THRESHOLD") and OPT["CUT_THRESHOLD"]:
            raw = cut_threshold(raw, thld)
    else:
        func = purity

    popt, pcov = curve_fit(
        func,
        raw_x[raw_max - buffer1 : raw_max + buffer2],
        raw[raw_max - buffer1 : raw_max + buffer2],
        p0=initial,
    )

    perr = np.sqrt(np.diag(pcov))

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        show_fit(info, raw, raw_x, purity, (run, ch, key), raw_max=raw_max, buffer1=buffer1, buffer2=buffer2, param=popt, OPT=OPT, save=save, debug=debug)

    return purity(raw_x, *popt), raw, popt, perr, labels


def simple_purity_fit(info, labels, raw, raw_x, fit_range, thld=1e-6, i_param={}, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """

    run, ch, key = labels
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    initial = []
    labels = ["PED", "T0", "A0", "A1", "SIGMA", "QUENCH"]
    for init in labels:
        if init not in i_param:
            if init == "PED":
                initial.append(np.mean(raw[: raw_max - buffer1]))
            if init == "T0":
                initial.append(raw_x[raw_max])
            rprint("[red]Initial parameter %s not found in i_param, using default value[/red]" % init)
        else:
            initial.append(i_param[init])

    if check_key(OPT, "CUT_THRESHOLD") and OPT["CUT_THRESHOLD"]:
        rprint("Cutting threshold at %.2E" % thld)
        ana = cut_threshold(raw, thld)

    if check_key(OPT, "FILTER") and OPT["FILTER"]:
        rprint(
            "Filtering the signal with a gaussian filter of sigma = %i" % OPT["FILTER_SIGMA"]
        )
        ana = gaussian_filter1d(ana, sigma=OPT["FILTER_SIGMA"])

    if check_key(OPT, "LOGY") and OPT["LOGY"]:        
        popt, pcov = curve_fit(
            logsimple_purity,
            raw_x[raw_max - buffer1 : raw_max + buffer2],
            np.log(ana[raw_max - buffer1 : raw_max + buffer2]),
            p0=initial,
        )

    else:
        popt, pcov = curve_fit(
            simple_purity,
            raw_x[raw_max - buffer1 : raw_max + buffer2],
            ana[raw_max - buffer1 : raw_max + buffer2],
            p0=initial,
        )

    perr = np.sqrt(np.diag(pcov))

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(OPT, "SHOW") == False:
        show_fit(info, raw, raw_x, simple_purity, (run, ch, key), raw_max=raw_max, buffer1=buffer1, buffer2=buffer2, thld=thld, param=popt, OPT=OPT, save=save, debug=debug)

    return simple_purity(raw_x, *popt), raw, popt, perr, labels


def sc_fit(info, labels, raw, raw_x, fit_range, thld=1e-6, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):

    run, ch, key = labels
    # Prepare plot vis
    next_plot = False
    plt.rcParams["figure.figsize"] = [8, 8]

    t0 = np.argmax(raw)
    raw_x = np.arange(len(raw))
    initial = (1500, 150, t0, 8, -700, 300)
    # bounds = ([-200, 10, t0*0.1, 1, -1500, 10], [10000, 3000, t0*10, 20, 1500, 1000])
    labels = ["AMP", "tau1", "T0", "sigma", "AMP2", "tau2"]

    try:
        popt, pcov = curve_fit(
            scfunc,
            raw_x[fit_range[0] : fit_range[1]],
            raw[fit_range[0] : fit_range[1]],
            p0=initial,
            method="trf",
        )
        perr = np.sqrt(np.diag(pcov))
    except:
        rprint("[red]Fit did not succeed[/red]")
        popt = initial
        perr = np.zeros(len(initial))

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(
        OPT, "SHOW"
    ) == False:
        show_fit(
            info,
            raw,
            raw_x,
            scfunc,
            (run, ch, key),
            raw_max=t0,
            buffer1=fit_range[0],
            buffer2=fit_range[1],
            param=popt,
            thld=thld,
            OPT=OPT,
            save=save,
            debug=debug,
        )

    aux = scfunc(raw_x, *popt)
    # rprint("\n")
    return aux, raw, popt, perr, labels


def fit_wvfs(
    my_runs,
    info,
    signal_type,
    thld,
    fit_range=[0, 200],
    i_param={},
    in_key=["ADC"],
    out_key="",
    OPT:Optional[dict]=None,
    save:bool=False,
    debug:bool=False,
):
    """
    \nDOC
    """
    if OPT is None:
        OPT = {}

    fit_dict, ref_dict, popt_dict, perr_dict, label_dict = {}, {}, {}, {}, {}
    i_param = get_initial_parameters(i_param)
    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(
        OPT, "SHOW"
    ) == False:
        plt.ion()

    for run, ch, key in product(my_runs["NRun"], my_runs["NChannel"], in_key):
        aux = dict()
        ref = dict()
        raw = my_runs[run][ch][key]
        raw_x = my_runs[run][ch]["Sampling"] * np.arange(len(raw[0]))

        for i in range(len(raw)):
            raw_max = np.max(raw[i])
            raw[i] = raw[i] / raw_max
            if signal_type == "SiPM":
                fit, new_raw, popt, perr, labels = sipm_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, thld, OPT, save, debug
                )
            elif signal_type == "SC":
                fit, new_raw, popt, perr, labels = sc_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, thld, OPT, save, debug
                )
            elif signal_type == "Scint":
                fit, new_raw, popt, perr, labels = scint_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, thld, i_param, OPT, save, debug
                )
            elif signal_type == "Purity":
                fit, new_raw, popt, perr, labels = purity_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, thld, i_param, OPT, save, debug
                )
            elif signal_type == "Quenching":
                fit, new_raw, popt, perr, labels = simple_purity_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, thld, i_param, OPT, save, debug
                )
            elif signal_type == "SimpleScint":
                fit, new_raw, popt, perr, labels = simple_scint_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, i_param, OPT, save, debug
                )
            elif signal_type == "TauSlow":
                fit, new_raw, popt, perr, labels = tau_fit(
                    info, (run, ch, key), raw[i], raw_x, fit_range, i_param, OPT, save, debug
                )
            else:
                rprint("[red]Fit type not recognized[/red]")
                return
            
            aux[i] = fit * raw_max
            ref[i] = new_raw * raw_max
            raw[i] = raw[i] * raw_max
            i_idx, f_idx = find_amp_decrease(aux[i], 1e-3)
            PE = np.sum(raw[i])
            PE_std = np.std(raw[i][:i_idx])

            folder_path = (
                f'{root}/{info["OUT_PATH"][0]}/analysis/fits/run{run}/ch{ch}/'
            )
            if not os.path.exists(folder_path):
                os.makedirs(name=folder_path, mode=0o777, exist_ok=True)
                os.chmod(folder_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

            term_output = ""
            term_output = term_output + "Fitting wvf %s for run %s, ch %s\n" % (
                i,
                run,
                ch,
            )
            term_output = term_output + "--------------------------------\n"
            for i in range(len(labels)):
                term_output = term_output + "%s:\t%.2E\t%.2E\n" % (
                    labels[i],
                    popt[i],
                    perr[i],
                )
            term_output = term_output + "--------------------------------\n"
            if (
                check_key(OPT, "TERMINAL_OUTPUT") == True
                and OPT["TERMINAL_OUTPUT"] == True
            ):
                rprint(term_output)

            if save:
                with open(f"{folder_path}/{signal_type}Fit_{run}_{ch}.txt", "w+") as f:
                    if signal_type == "Scint" or signal_type == "SimpleScint":
                        f.write("%s:\t%.2f\t%.2f\n" % ("PE", PE, PE_std))
                    for i in range(len(labels)):
                        f.write("%s:\t%.4E\t%.4E\n" % (labels[i], popt[i], perr[i]))
                if debug:
                    rprint("File saved in: %s" % folder_path)

        fit_dict[(run, ch, key)] = fit
        ref_dict[(run, ch, key)] = ref
        popt_dict[(run, ch, key)] = popt
        perr_dict[(run, ch, key)] = perr
        label_dict[(run, ch, key)] = labels
        my_runs[run][ch]["Fit" + signal_type + out_key] = aux
        my_runs[run][ch]["Ref" + signal_type + out_key] = ref
    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(
        OPT, "SHOW"
    ) == False:
        plt.ioff()
    return fit_dict, ref_dict, popt_dict, perr_dict, label_dict


def show_fit(info, raw, raw_x, func, labels, raw_max, buffer1, buffer2, param, thld=1e-6, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """
    run, ch, key = labels
    fig = plt.figure()
    plt.title(f"Fit full wvf {key} with {OPT['SCINT_FIT'] if 'SCINT_FIT' in OPT else 'default'}")
    plt.plot(raw_x, raw, zorder=0, label="raw", c=colors[int(ch)-2])
    
    if check_key(OPT, "CUT_THRESHOLD") and OPT["CUT_THRESHOLD"]:
        ana = cut_threshold(raw, thld)
        plt.axhline(thld, ls=":", c="k")
    else:
        ana = raw.copy()
    
    if check_key(OPT, "FILTER") and OPT["FILTER"]:
        plt.plot(raw_x, gaussian_filter1d(ana, sigma=OPT["FILTER_SIGMA"]), zorder=1, label="ana", c=colors[int(ch)-1])

    plt.plot(raw_x[raw_max-buffer1:], func(raw_x[raw_max-buffer1:], *param),  ls = "--", c="red", label="fit")
    plt.xlabel("Time in [s]"); plt.ylabel("ADC Counts")
    plt.axvline(raw_x[raw_max-buffer1], ls = ":", c = "k")
    plt.axvline(raw_x[raw_max+buffer2], ls = ":", c = "k")
    
    if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
        plt.semilogy()
        plt.ylim(thld, raw[raw_max]*2)
    
    plt.legend()
    
    while not plt.waitforbuttonpress(-1):
        pass
    
    if save:
        save_figure(fig, f"{info['OUT_PATH'][0]}/images", run, ch, OPT["SCINT_FIT"], debug=debug)
    
    plt.clf()
    plt.close(fig)


def get_initial_parameters(i_param):
    """
    \nDOC
    """

    # Define input parameters from dictionary
    if check_key(i_param, "ped") == False:
        i_param["ped"] = 1e-6
    if check_key(i_param, "t0") == False:
        i_param["t0"] = 1e-6
    if check_key(i_param, "sigma") == False:
        i_param["sigma"] = 1e-8
    if check_key(i_param, "const") == False:
        i_param["const"] = 1e-8
    if check_key(i_param, "a_fast") == False:
        i_param["a_fast"] = 1e-2
    if check_key(i_param, "tau_fast") == False:
        i_param["tau_fast"] = 1e-8
    if check_key(i_param, "a_slow") == False:
        i_param["a_slow"] = 1e-2
    if check_key(i_param, "tau_slow") == False:
        i_param["tau_slow"] = 1e-6

    return i_param


def scint_profile(x, const, a_f, tau_f, tau_s):
    return const * (
        2 * a_f / tau_f * np.exp(-(x) / tau_f)
        + 2 * (1 - a_f) / tau_s * np.exp(-(x) / tau_s)
    )


def log_scint_profile(x, const, a_f, tau_f, tau_s):
    return np.log(scint_profile(x, const, a_f, tau_f, tau_s))


def tau_slow_profile(x, a_s, tau_s):
    return 2 * a_s / tau_s * np.exp(-(x) / tau_s)


def log_tau_slow_profile(x, a_s, tau_s):
    y = np.log(tau_slow_profile(x, a_s, tau_s))
    # Replace infs and nans from the array by 0
    y[np.isinf(y)] = 0
    y[np.isnan(y)] = 0
    return y


def simple_scint_fit(info, labels, raw, raw_x, fit_range, i_param={}, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """
    run, ch, key = labels
    next_plot = False
    thld = 1e-10
    for i in range(len(raw)):
        if raw[i] <= thld:
            raw[i] = thld
        if np.isnan(raw[i]):
            raw[i] = thld
    # Define input parameters from dictionary
    const = i_param["const"]
    a_fast = i_param["a_fast"]
    tau_fast = i_param["tau_fast"]
    a_slow = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]

    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    a1 = a_fast
    a1_low = a1 * 0.9
    a1_high = a1 * 1.1
    tau1 = tau_fast
    tau1_low = tau1 * 0.9
    tau1_high = tau1 * 1.1

    a2 = a_slow
    a2_low = a_slow * 1e-2
    a2_high = a_slow * 1e2
    tau2 = tau_slow
    tau2_low = tau_slow * 1e-2
    tau2_high = tau_slow * 1e2

    const_high = const * 100
    const_low = const * 0.01

    bounds2 = (
        [const_low, a1_low, tau1_low, tau2_low],
        [const_high, a1_high, tau1_high, tau2_high],
    )
    initial2 = (const, a1, tau1, tau2)
    labels2 = ["CONST", "AMP1", "TAU1", "TAU2"]

    # try:
    # popt, pcov = curve_fit(scint_profile, raw_x[:buffer2] ,raw[raw_max:raw_max+buffer2],p0=initial2, bounds=bounds2)
    popt, pcov = curve_fit(
        log_scint_profile,
        raw_x[:buffer2],
        np.log(raw[raw_max : raw_max + buffer2]),
        p0=initial2,
        bounds=bounds2,
    )
    perr = np.sqrt(np.diag(pcov))

    # except:
    # rprint("Fit could not be performed")
    # popt2 = initial2
    # perr2 = np.zeros(len(popt2))
    zeros_aux = np.zeros(raw_max)
    zeros_aux2 = np.zeros(len(raw) - raw_max - buffer2)

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(
        OPT, "SHOW"
    ) == False:
        show_fit(raw, raw_x, scint_profile, raw_max=raw_max, buffer1=buffer1, buffer2=buffer2, param=popt, OPT=OPT, save=save, debug=debug)

    aux = np.concatenate([zeros_aux, scint_profile(raw_x[:buffer2], *popt), zeros_aux2])
    return aux, raw, popt, perr, labels2


def tau_fit(info, labels, raw, raw_x, fit_range, i_param={}, OPT:Optional[dict]=None, save:bool=False, debug:bool=False):
    """
    \nDOC
    """

    run, ch, key = labels
    if OPT == None:
        OPT = {}

    next_plot = False

    # Define input parameters from dictionary
    a_slow = i_param["a_slow"]
    tau_slow = i_param["tau_slow"]

    # Find peak and perform fit
    raw_max = np.argmax(raw)
    buffer1 = fit_range[0]
    buffer2 = fit_range[1]

    # USING VALUES FROM FIRST FIT PERFORM SECONG FIT FOR THE SLOW COMPONENT
    a2 = a_slow
    a2_low = a_slow * 1e-2
    a2_high = a_slow * 1e2
    tau2 = tau_slow
    tau2_low = tau_slow * 1e-2
    tau2_high = tau_slow * 1e2

    bounds2 = ([a2_low, tau2_low], [a2_high, tau2_high])
    labels2 = ["AMP2", "TAU2"]
    initial2 = (a2, tau2)
    # try:
    # popt, pcov = curve_fit(scint_profile, raw_x[:buffer2] ,raw[raw_max:raw_max+buffer2],p0=initial2, bounds=bounds2)
    y = np.log(raw[buffer1 : buffer2])
    y[np.isinf(y)] = 0
    y[np.isnan(y)] = 0
    popt, pcov = curve_fit(
        log_tau_slow_profile, raw_x[: buffer2 - buffer1], y, p0=initial2, bounds=bounds2
    )
    perr = np.sqrt(np.diag(pcov))

    # except:
    # rprint("Fit could not be performed")
    # popt2 = initial2
    # perr2 = np.zeros(len(popt2))
    zeros_aux = np.zeros(buffer1)
    zeros_aux2 = np.zeros(len(raw) - buffer2)

    if (check_key(OPT, "SHOW") == True and OPT["SHOW"] == True) or check_key(
        OPT, "SHOW"
    ) == False:
        # rprint("SHOW key not included in OPT")
        # CHECK FIRST FIT
        tau_slow_fit = tau_slow_profile(raw_x[: buffer2 - buffer1], *popt)
        
        fig = plt.figure()
        plt.subplot(1, 1, 1)
        plt.title("%s - Tau fit - run %s" %(key, run))
        
        if check_key(OPT, "MICRO_SEC") == True and OPT["MICRO_SEC"] == True:
            plt.xlabel(r"Time [$\mu$s]")
            raw_x = raw_x* 1e6
        
        else:
            plt.xlabel("Time in [s]")
        
        plt.ylabel("ADC Counts")
        plt.plot(raw_x, raw, label="Raw - ch%s" %(ch), c=get_prism_colors()[int(ch)])
        plt.plot(
            raw_x,
            np.concatenate(
                [
                    zeros_aux,
                    tau_slow_fit,
                    zeros_aux2,
                ]
            ),
            label="TauFit",
            c="red"
        )
        # plt.axvline(raw_x[-buffer2], ls = "--", c = "k")
        if check_key(OPT, "LOGY") == True and OPT["LOGY"] == True:
            plt.semilogy()
        plt.legend()
        if save:
            save_figure(fig, f"{root}/{info['OUT_PATH'][0]}/images", run, ch, f"{key}_TauFit", debug=debug)
        
        while not plt.waitforbuttonpress(-1):
            pass
        plt.clf()
    plt.close()

    aux = np.concatenate(
        [zeros_aux, tau_slow_profile(raw_x[: buffer2 - buffer1], *popt), zeros_aux2]
    )
    return aux, raw, popt, perr, labels2
