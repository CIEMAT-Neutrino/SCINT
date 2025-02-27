import sys

sys.path.insert(0, "../")
from lib.io_functions import load_npy, save_proccesed_variables
from lib.fit_functions import scfunc, gauss
from lib.sim_functions import rand_scint_times
from lib.wvf_functions import find_baseline_cuts, find_amp_decrease
from lib.dec_functions import deconvolve

import uproot
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from scipy.optimize import curve_fit

plt.rcParams.update({"font.size": 15})

info = {"PATH": ["../_data/"], "MONTH": ["SC_Test"]}

my_run = load_npy([1, 2, 3], [500, 600, 700, 800, 900, 1000], preset="ALL", info=info)

templates = [
    "Only Input Transformer (reduce undershoot)",
    "Original Input",
    "Input Capacitor 100n (extra reduce undershoot)",
]
# my_run = load_npy([1],[500], preset="ALL", info=info)
MC_num = 1000  # Number of mc wvf to be generated
out_file = open(info["PATH"][0] + "SC_Test/results/results.txt", mode="w+")
out_file.write("Label\tTemplate\tWindow Length [ticks]\tMEAN\tSTD\n")

for run, ch in product(my_run["NRun"], my_run["NChannel"]):
    dec_key = "DecNoiseADC"
    sigma = [50, 50]
    num = np.random.randint(0, MC_num)

    for filter_key in ["Raw", "Gauss", "Wiener"]:
        if filter_key == "Raw":
            color = "tab:blue"
        if filter_key == "Gauss":
            color = "tab:green"
        if filter_key == "Wiener":
            color = "tab:orange"

        key_value = [filter_key + "Amp", filter_key + "Charge", filter_key + "Time"]
        x_label = ["Amp in a.u.", "Charge in [PE]", "Time in [ns]"]

        fig, ax = plt.subplots(1, 4, figsize=(25, 5))
        if filter_key == "Raw":
            ax[0].plot(
                1e6
                * my_run[run][ch]["Sampling"]
                * np.arange(len(my_run[run][ch]["McNoiseADC"][num])),
                my_run[run][ch]["McNoiseADC"][num],
                c="tab:blue",
                label="MC NOISE",
                alpha=0.75,
            )

        else:
            ax[0].plot(
                1e6
                * my_run[run][ch]["Sampling"]
                * np.arange(len(my_run[run][ch][filter_key + dec_key][num])),
                my_run[run][ch][filter_key + dec_key][num],
                c=color,
                label="MC NOISE",
            )

        for i in range(1, len(ax)):
            if i == 1 or i == 2:
                n, bins, patches = ax[i].hist(
                    my_run[run][ch][key_value[i - 1]], bins=30, alpha=0.75, color=color
                )
                initial = [np.max(n), bins[np.argmax(n) + 1], sigma[i - 1]]
                gauss_fit_labels = ["Amp:\t", "Mean:\t", "Sigma:\t"]
                try:
                    popt2, pcov2 = curve_fit(gauss, bins[:-1], n, p0=initial)
                except:
                    print("FIT COULD NOT BE PERFORMED")
                    popt2 = initial
                # for j in range(len(popt2)): print(gauss_fit_labels[j],"{:.2E}".format(popt2[j]))
                ax[i].axvline(
                    popt2[1], c="grey", ls="--", label="MEAN: %.2f" % abs(popt2[1])
                )
                ax[i].plot(
                    bins + (bins[1] - bins[0]) / 2,
                    gauss(bins, *popt2),
                    c="red",
                    label="SIGMA: %.2f %%" % abs(100 * popt2[2] / popt2[1]),
                )

            else:
                n, bins, patches = ax[i].hist(
                    my_run[run][ch][key_value[i - 1]],
                    bins=np.linspace(0, np.max(my_run[run][ch][key_value[i - 1]]), 30),
                    alpha=0.75,
                    color=color,
                )
                ax[i].axvline(
                    bins[np.argmax(n)] + bins[1] / 2,
                    c="grey",
                    ls=":",
                    label="MODE: %.2f" % (bins[np.argmax(n)] + bins[1] / 2),
                )
                ax[i].axvline(
                    np.mean(my_run[run][ch][key_value[i - 1]]),
                    c="grey",
                    label="MEAN: %.2f" % np.mean(my_run[run][ch][key_value[i - 1]]),
                )
                ax[i].axvline(
                    np.mean(my_run[run][ch][key_value[i - 1]])
                    + np.std(my_run[run][ch][key_value[i - 1]]),
                    c="grey",
                    ls="--",
                    label="STD: %.2f" % np.std(my_run[run][ch][key_value[i - 1]]),
                )
                ax[i].axvline(
                    np.mean(my_run[run][ch][key_value[i - 1]])
                    - np.std(my_run[run][ch][key_value[i - 1]]),
                    c="grey",
                    ls="--",
                    label="STD: %.2f" % np.std(my_run[run][ch][key_value[i - 1]]),
                )

            ax[i].legend()
            ax[i].set_title(key_value[i - 1])
            ax[i].set_xlabel(x_label[i - 1])
            ax[i].set_ylabel("Counts")
            ax[i].grid(True, which="both")

        ax[0].grid(True)
        ax[0].axhline(0, ls="--", c="grey")
        ax[0].set_title("Example" + filter_key + "Wvf")
        ax[0].set_xlabel("Time in [us]")
        ax[0].set_ylabel("Amp in [a.u.]")
        plt.savefig(
            info["PATH"][0]
            + "SC_Test/results/%sWvf_%i_array_%i_us" % (filter_key, run, ch)
        )
        plt.close()
        out_file.write(
            "%s\t%s\t%i\t%f\t%f\n"
            % (filter_key, templates[run - 1], ch, popt2[1], popt2[2])
        )
out_file.close()
