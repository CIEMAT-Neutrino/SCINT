import numpy as np
from rich import print as print

# Imports from other libraries
from numba_stats import (
    norm,
    expon,
)  # uniform,truncexpon,poisson,qgaussian #https://github.com/HDembinski/numba-stats/tree/main/src/numba_stats

from srcs.utils import get_project_root
from .io_functions import print_colored
from .fit_functions import gaussian, gaussian_train

root = get_project_root()


def rand_scint_times(n, fast=6e-9, slow=1.4e-6, ratio=0.23):
    """
    \nThis function is a randon number generator that returns a sorted nparray of photon arrival times according to a given scintilation profile.
    \n**VARIABLES**:
    \n - n: (int) number of produced times.
    \n - fast: (float) tau value of fast scint component -- default: 6e-9 [s]
    \n - slow: (float) tau value of slow scint component -- default: 1e-6 [s]
    \n - ratio: (float) ratio of the slow scint components sholud be [0,1] -- default: 0.23
    \n***Values adopted from: Enhancement of the X-Arapuca photon detection device for the DUNE experiment, Journal of Instrumentation, vol. 16, p. P09027, sep (2021).
    """

    if ratio < 0 or ratio > 1:
        print_colored("WARNING: ratio should be between 0 and 1!!!", "WARNING")

    aux = np.random.uniform(low=0, high=1, size=n)
    # offset = np.random.random() #photon can arrive at any time
    array = (
        fast
        + (aux > (ratio)) * np.random.exponential(scale=fast, size=n)
        + (aux < (ratio)) * np.random.exponential(scale=slow, size=n)
    )
    array = np.sort(array)

    return array


def larsoft_template(
    time_in_us, fPeakTime, fVoltageToADC, fMaxAmplitude, fFrontTime, fBackTime
):
    template = []
    for i in time_in_us:
        if i < fPeakTime:
            template.append(
                fVoltageToADC * fMaxAmplitude * np.exp((i - fPeakTime) / fFrontTime)
            )
        else:
            template.append(
                fVoltageToADC * fMaxAmplitude * np.exp(-(i - fPeakTime) / fBackTime)
            )

    return np.asarray(template)


# ===========================================================================#
# *************************** EMPIRICAL FUNCTIONS ***************************#
# ===========================================================================#


def expand_bins(bins, data):
    if np.max(bins) > np.max(data) and np.min(bins) < np.min(data):
        pass
    elif np.max(bins) > np.max(data):
        bin_width = bins[1] - bins[0]
        bins = np.arange(np.min(data), np.max(bins) + bin_width, bin_width)
    elif np.min(bins) < np.min(data):
        bin_width = bins[1] - bins[0]
        bins = np.arange(np.min(bins), np.max(data) + bin_width, bin_width)
    return bins


def interpolate_sim_data(bins, path, percentile=(1, 99)):
    data = np.load(path)
    data = data[
        (data > np.percentile(data, percentile[0]))
        & (data < np.percentile(data, percentile[1]))
    ]
    if type(bins) == int:
        hist, bin_edges = np.histogram(data, bins=bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    elif type(bins) == np.ndarray:
        bins = expand_bins(bins, data)
        hist, bin_edges = np.histogram(data, bins=bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    return bin_centers, hist


def combi_convolve_poisson(bins, height, eff):
    from scipy.stats import poisson
    from scipy.interpolate import interp1d

    path = f"{root}/data/MegaCell_LAr/Dic23/sim/combi.npy"
    bin_centers, hist = interpolate_sim_data(50, path)
    new_bins = np.arange(int(np.min(bins)), int(np.max(bins) + 1))
    convolved_hist = np.zeros(len(new_bins))
    for i in range(len(hist)):
        convolved_hist += hist[i] * poisson.pmf(new_bins, eff * bin_centers[i])
    # Interpolate the convolved histogram to the original binning
    f = interp1d(
        new_bins,
        convolved_hist,
        kind="cubic",
        fill_value="extrapolate",
        bounds_error=False,
    )
    convolved_hist = f(bins)
    return height * convolved_hist / np.max(convolved_hist)


def sipm1_convolve_poisson(bins, height, eff):
    from scipy.stats import poisson
    from scipy.interpolate import interp1d

    path = f"{root}/data/MegaCell_LAr/Dic23/sim/sipm1.npy"
    bin_centers, hist = interpolate_sim_data(50, path)
    new_bins = np.arange(int(np.min(bins)), int(np.max(bins) + 1))
    convolved_hist = np.zeros(len(new_bins))
    for i in range(len(hist)):
        convolved_hist += hist[i] * poisson.pmf(new_bins, eff * bin_centers[i])
    # Interpolate the convolved histogram to the original binning
    f = interp1d(
        new_bins,
        convolved_hist,
        kind="cubic",
        fill_value="extrapolate",
        bounds_error=False,
    )
    convolved_hist = f(bins)
    return height * convolved_hist / np.max(convolved_hist)


def fitting_function(function, debug=False):
    if function == "megacell_v3":
        return combi_convolve_poisson
    if function == "megacell_v3_sipm1":
        return sipm1_convolve_poisson
    if function == "norm_gaussian":
        return norm.pdf
    if function == "exponential":
        return expon.pdf
    else:
        if debug:
            print_colored(
                "Not configured, looking for a local defined function", color="WARNING"
            )
        try:
            function = globals()[function]
            return function
        except KeyError:
            print_colored("Function (%s) not found" % function, color="ERROR")
            pass


def setup_fitting_function(function_name, ydata, xdata, debug=False):
    function = fitting_function(function_name, debug=debug)
    if function_name == "gaussian" or "megacell_v3" in function_name:
        ydata = ydata / np.max(ydata)
        return function, ydata
    elif function_name == "norm_gaussian":
        ydata = ydata / np.sum(ydata * (xdata[1] - xdata[0]))
        return function, ydata
    else:
        return function, ydata
