import os
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("Qt5Agg")

from jacobi import propagate
from iminuit import Minuit, cost

from src.utils import get_project_root
from .io_functions import write_output_file, read_yaml_file, print_colored
from .sty_functions import add_grid, get_color, style_selector
from .sim_functions import setup_fitting_function, fitting_function
from .fit_functions import gaussian, gaussian_train
from .ana_functions import get_unit

root = get_project_root()


def initial_values(data, function, debug: bool = False):
    my_fits = read_yaml_file("FitConfig", path=f"{root}/config/", debug=debug)
    ini_fun = my_fits[function]
    data_s = ", ".join(map(str, data))
    data_s = "[" + data_s + "]"
    ini_val = [eval(f"{i}({data_s})") if isinstance(i, str) else i for i in ini_fun]
    if "np.std" in ini_fun:
        std_idx = ini_fun.index("np.std")
        ini_val[std_idx] = ini_val[std_idx] / 2
    # if debug: print_colored("Initial values: " +str(ini_val), "DEBUG")
    return ini_val


def minuit_fit(data, OPT, debug: bool = False):
    """
    \nThis function performs a fit to the data, using the function specified in the input using MINUIT.
    \nIt returns the parameters of the fit (if performed)
    """
    ydata, bins = np.histogram(data, bins=OPT["ACCURACY"])
    xdata = bins[:-1] + (bins[1] - bins[0]) / 2

    print_colored(f"DEFAULT MINUIT BINNED FIT ({OPT['FIT']})", "WARNING")
    ini_val = initial_values(data, OPT["FIT"], debug=debug)

    function, norm_ydata = setup_fitting_function(OPT["FIT"], ydata, xdata, debug=debug)
    c = cost.LeastSquares(xdata, norm_ydata, np.sqrt(norm_ydata), function)
    m = Minuit(c, *ini_val)
    # Generate limits going from 0 to 1.5 times the initial value
    m.migrad()  # find minimum
    m.hesse()  # accurate error estimates
    # m.minos()  # accurate error estimates
    if debug:
        print_colored("Fitting with Minuit", "INFO", styles=["bold"])
        print(m.hesse())
    return m, xdata, norm_ydata


def percentile_cut(data, percentile):
    ypbot = np.percentile(data, percentile[0])
    yptop = np.percentile(data, percentile[1])
    return data[(data >= ypbot) & (data <= yptop)]


def save_fit_parameters(run, ch, m_fit, fit_function, variable, info, user_input):
    parameters = [
        [[m_fit.values[idx], m_fit.errors[idx]] for idx in range(len(m_fit.values))]
    ]
    header = [
        (
            m_fit.parameters[int(idx / 2)].upper()
            if idx % 2 == 0
            else "D" + m_fit.parameters[int(idx / 2)].upper()
        )
        for idx in range(len(m_fit.values) * 2)
    ]
    write_output_file(
        run,
        ch,
        output=parameters,
        filename=fit_function + variable,
        header_list=header,
        info=info,
        not_saved=[],
        debug=user_input["debug"],
    )


def plot_minuit_fit(m_fit, xdata, ydata, labels, user_input, info, OPT):
    run, ch, variable = labels
    variable_units = get_unit(variable)
    fit_function = OPT["FIT"]
    style_selector(OPT)

    plt.ion()
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    plt.title(f"run{run} ch{ch} {variable} Fit".format(variable))
    plt.xlabel(variable_units)
    plt.ylabel("Norm Counts")

    y_fit, ycov = propagate(
        lambda p: fitting_function(OPT["FIT"], debug=False)(xdata, *p),
        m_fit.values,
        m_fit.covariance,
    )

    legend = [
        f"{m_fit.parameters[m]} = {value:.1e} $\pm$ {m_fit.errors[m]:.1e}"
        for m, value in enumerate(m_fit.values)
    ]
    legend.append(r"$\chi^2$ = %.2f" % (m_fit.fval))

    print(ydata[-2:], y_fit[-2:])
    plt.hist(
        xdata,
        xdata,
        weights=ydata,
        label="run {} ch {}".format(run, ch),
        histtype="step",
        align="left",
        color=get_color(ch, even=True),
    )
    plt.hist(
        xdata,
        xdata,
        weights=y_fit,
        label=f"{OPT['FIT']} fit:",
        histtype="step",
        align="left",
        color="red",
    )
    plt.axvline(
        xdata[int(len(xdata) / 2)], color="white", label="\n".join(legend), alpha=0
    )

    yerr = np.sqrt(np.diag(ycov))
    plt.fill_between(
        xdata,
        (y_fit - yerr),
        (y_fit + yerr),
        alpha=0.2,
        color=get_color(ch, even=False),
    )
    plt.legend()
    plt.setp(ax.get_legend().get_texts(), fontsize="12")
    # Force x axis tcks to be scintific notation
    plt.ticklabel_format(axis="x", style="sci")

    # Change font size for legend
    matplotlib.rcParams.update({"font.size": 11})
    # Pin legend to the upper left corner
    plt.legend(loc="lower center")
    plt.show()
    while not plt.waitforbuttonpress(-1):
        pass
    plt.close()

    if user_input["save"]:
        fig.savefig(
            f'{root}/{info["OUT_PATH"][0]}/images/run{run}_ch{ch}_{variable}_Fit.png',
            dpi=500,
        )
        try:
            os.chmod(
                f'{root}/{info["OUT_PATH"][0]}/images/run{run}_ch{ch}_{variable}_Fit.png',
                0o770,
            )
        except:
            pass

        save_fit_parameters(run, ch, m_fit, OPT["FIT"], variable, info, user_input)
        if user_input["debug"]:
            print(
                f"Saving plot in {root}/{info['PATH'][0]}/images/run{run}_ch{ch}_{variable}_{fit_function}_Fit.png"
            )
