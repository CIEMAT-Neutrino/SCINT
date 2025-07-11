from rich import print as rprint    
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from typing import Optional
from jacobi import propagate
from iminuit import Minuit, cost

from srcs.utils import get_project_root
from .io_functions import write_output_file, read_yaml_file, save_figure
from .sty_functions import add_grid, get_color, style_selector, get_prism_colors
from .sim_functions import setup_fitting_function, fitting_function
from .unit_functions import get_unit

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
    # if debug: print("Initial values: " +str(ini_val))
    return ini_val


def minuit_fit(data, OPT, export: bool = False, debug: bool = False):
    """This function performs a fit to the data, using the function specified in the input using MINUIT. It returns the parameters of the fit (if performed)
    
    :param data: data to fit
    :type data: np.array
    :param OPT: dictionary containing the options
    :type OPT: dict
    :param debug: debug flag, defaults to False
    :type debug: bool, optional
    
    :return: m, xdata, norm_ydata -- fit parameters, xdata and normalized ydata
    """
    data = percentile_cut(data, OPT["PERCENTILE"])
    bins = OPT["ACCURACY"]
    if OPT["PE"]:
        bins = np.arange(int(np.min(data)), int(np.max(data)) + 1)
    ydata, bins = np.histogram(data, bins=bins)
    xdata = bins[:-1] + (bins[1] - bins[0]) / 2

    rprint(f"[yellow]DEFAULT MINUIT BINNED FIT ({OPT['FIT']})[/yellow]")
    ini_val = initial_values(data, OPT["FIT"], debug=debug)

    function, norm_ydata = setup_fitting_function(OPT["FIT"], ydata, xdata, debug=debug)
    c = cost.LeastSquares(xdata, norm_ydata, np.sqrt(norm_ydata), function)
    m = Minuit(c, *ini_val)
    # Generate limits going from 0 to 1.5 times the initial value
    m.migrad()  # find minimum
    m.hesse()  # accurate error estimates
    # m.minos()  # accurate error estimates
    if debug:
        print("[cyan,bold]Fitting with Minuit[/cyan,bold]")
        print(m.hesse())

    return m, xdata, norm_ydata


def export_minuit_fit(m_fit, xdata, ydata, labels:tuple, info, OPT:Optional[dict] = None, debug: bool = False):
    """This function exports the fit parameters to a file, if the user has requested it.
    
    :param m_fit: fit parameters
    :type m_fit: Minuit object
    :param xdata: x data
    :type xdata: np.array
    :param ydata: y data
    :type ydata: np.array
    :param labels: labels for the plot
    :type labels: tuple (run, channel, variable)
    :param user_input: user input dictionary
    :type user_input: dict
    
    """

    run, ch, variable = labels
    yfit, ycov = propagate(
        lambda p: fitting_function(OPT["FIT"], debug=False)(xdata, *p),
        m_fit.values,
        m_fit.covariance,
    )
    yerr = np.sqrt(np.diag(ycov))

    # Export the data xdata, ydata, and the yfit to a file so that there is a header and the data is saved in a readable format
    if debug:
        print(f"[cyan,bold]Exporting fit parameters for run {run}, channel {ch}, variable {variable}[/cyan,bold]")
    # parameters = [
    #     [[x, 0] for x in xdata].T,
    #     [[y, 1/np.sqrt(y)] for y in ydata].T,
    #     [[y, dy] for y, dy in zip(yfit, yerr)].T,
    # ]
    parameters = [
        [[x, 0],[y, dy],[fit, dfit]] for x, y, fit, dy, dfit in zip(xdata, ydata, yfit, np.sqrt(ydata), yerr)
    ]
    header = ["PE", "DPE", "AMP", "DAMP", "FIT", "DFIT"]
    write_output_file(
        run,
        ch,
        output=parameters,
        filename=f"{OPT['FIT']}_{variable}",
        header_list=header,
        info=info,  # Not used in this context
        not_saved=[],
        debug=debug,
    )


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
        filename=f"{fit_function}_{variable}_fit",
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
    
    if "+" in ch :
        ch_color = int(ch[-1])
    else:
        ch_color = int(ch)

    plt.ion()
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    plt.title(f"run{run} ch{ch} {variable} Fit".format(variable))
    if "Charge" in variable:
        plt.xlabel(f"Charge ({variable_units})")
    else:
        plt.xlabel(f"{variable} ({variable_units})")
    
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
    
    colors = get_prism_colors() + get_prism_colors()

    plt.hist(
        xdata,
        bins=len(xdata),
        weights=ydata,
        label="run {} ch {}".format(run, ch),
        histtype="step",
        align="left",
        color=colors[int(ch_color)],
    )
    plt.hist(
        xdata,
        bins=len(xdata),
        weights=y_fit,
        label=f"{OPT['FIT']} fit:",
        histtype="step",
        align="left",
        color="red",
    )
    yerr = np.sqrt(np.diag(ycov))
    plt.fill_between(
        xdata,
        (y_fit - yerr),
        (y_fit + yerr),
        alpha=0.2,
        color=colors[int(ch_color)],
    )
    if OPT["SHOW_LEGEND"]:
        if OPT["SHOW_FIT_PARAMETERS"]:
            plt.axvline(
                xdata[int(len(xdata) / 2)], color="white", label="\n".join(legend), alpha=0
            )
            # Pin legend to the upper left corner
            plt.legend(loc="lower center")

        plt.legend()
        plt.setp(ax.get_legend().get_texts(), fontsize="12")
        # Change font size for legend
        matplotlib.rcParams.update({"font.size": 11})
    
    else:
        plt.legend().set_visible(False)
    
    # Force x axis tcks to be scintific notation
    plt.ticklabel_format(axis="x", style="sci")

    plt.show()
    while not plt.waitforbuttonpress(-1):
        pass
    plt.close()

    if user_input["save"]:
        save_figure(fig, f'{root}/{info["OUT_PATH"][0]}/images/', run, ch, f'{variable}_Fit', debug=user_input["debug"])
        if user_input["debug"]:
            print(
                f"Saving plot in {root}/{info['OUT_PATH'][0]}/images/run{run}_ch{ch}_{variable}_{fit_function}_Fit.png"
            )

