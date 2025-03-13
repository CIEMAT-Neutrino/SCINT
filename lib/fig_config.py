tex_installed = False

import sys
import plotly.graph_objects as go

if not sys.platform.startswith("win"):
    import subprocess

    try:
        # print("WORKING ON WINDOWS")
        bashCommand = "yum info texlive-latex-base"
        process = subprocess.Popen(
            bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    except FileNotFoundError:
        # print("WORKING ON UBUNTU")
        bashCommand = "apt list --installed | grep texlive-latex-base"
        process = subprocess.Popen(
            bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
    output, error = process.communicate()
    if "Error" in str(output):
        print(
            "You don't have latex installed. Changing default configuration to tex=False"
        )
        tex_installed = False
    else:
        print("You have latex installed!. Applying default configuration (tex=True)")
        tex_installed = True

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def figure_features(tex=tex_installed, font="serif", dpi=600):
    """Customize figure settings.
    
    :param tex: use LaTeX, defaults to tex_installed
    :type tex: bool, optional
    :param font: font type, defaults to "serif"
    :type font: str, optional
    :param dpi: dots per inch, defaults to 600
    :type dpi: int, optional
    """

    plt.rcParams.update(
        {
            "font.size": 16,
            "font.family": font,
            "font.weight": "bold",
            "text.usetex": tex,
            "figure.subplot.top": 0.92,
            "figure.subplot.right": 0.95,
            "figure.subplot.left": 0.10,
            "figure.subplot.bottom": 0.12,
            "figure.subplot.hspace": 0.2,
            "figure.subplot.wspace": 0.2,
            "savefig.dpi": dpi,
            "savefig.format": "png",
            "axes.titlesize": 16,
            "axes.labelsize": 16,
            "axes.axisbelow": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 5,
            "xtick.minor.size": 2.25,
            "xtick.major.pad": 7.5,
            "xtick.minor.pad": 7.5,
            "ytick.major.pad": 7.5,
            "ytick.minor.pad": 7.5,
            "ytick.major.size": 5,
            "ytick.minor.size": 2.25,
            "xtick.labelsize": 15,
            "ytick.labelsize": 15,
            "legend.fontsize": 12,
            "legend.framealpha": 1,
            "figure.titlesize": 18,
            "lines.linewidth": 2,
            "figure.constrained_layout.use": True,
        }
    )


def add_grid(ax, lines=True, locations=None):
    """Add a grid to the current plot.
    
    :param ax: axis object in which to draw the grid.
    :type ax: Axis
    :param lines: add lines to the grid, defaults to True
    :type lines: bool, optional
    :param locations: (xminor, xmajor, yminor, ymajor), defaults to None
    :type locations: tuple, optional
    """

    if lines:
        ax.grid(lines, alpha=0.5, which="minor", ls=":")
        ax.grid(lines, alpha=0.7, which="major")

    if locations is not None:
        assert len(locations) == 4, "Invalid entry for the locations of the markers"

        xmin, xmaj, ymin, ymaj = locations
        ax.xaxis.set_minor_locator(MultipleLocator(xmin))
        ax.xaxis.set_major_locator(MultipleLocator(xmaj))
        ax.yaxis.set_minor_locator(MultipleLocator(ymin))
        ax.yaxis.set_major_locator(MultipleLocator(ymaj))


def format_coustom_plotly(
    fig: go.Figure,
    title: str = None,
    legend: dict = dict(),
    fontsize: int = 16,
    figsize: int = None,
    ranges: tuple = (None, None),
    matches: tuple = ("x", "y"),
    tickformat: tuple = (".s", ".s"),
    log: tuple = (False, False),
    margin: dict = {"auto": True},
    add_units: bool = True,
    debug: bool = False,
):
    """Format a plotly figure

    :param fig: plotly figure
    :type fig: go.Figure
    :param title: title of the figure, defaults to None
    :type title: str, optional
    :param legend: legend options, defaults to dict()
    :type legend: dict, optional
    :param fontsize: font size, defaults to 16
    :type fontsize: int, optional
    :param figsize: figure size, defaults to None
    :type figsize: tuple, optional
    :param ranges: axis ranges, defaults to (None,None)
    :type ranges: tuple, optional
    :param matches: axis matches, defaults to ("x","y")
    :type matches: tuple, optional
    :param tickformat: axis tick format, defaults to ('.s','.s')
    :type tickformat: tuple, optional
    :param log: axis log scale, defaults to (False,False)
    :type log: tuple, optional
    :param margin: figure margin, defaults to {"auto":True}
    :type margin: dict, optional
    :param add_units: True to add units to axis labels, False otherwise, defaults to True
    :type add_units: bool, optional
    :param debug: True to print debug statements, False otherwise, defaults to False
    :type debug: bool, optional
    
    :return: plotly figure
    :rtype: go.Figure
    """

    # Find the number of subplots
    if type(fig) == go.Figure:
        try:
            rows, cols = fig._get_subplot_rows_columns()
            rows, cols = rows[-1], cols[-1]
        except Exception:
            rows, cols = 1, 1
            print("[red]Error: unknown figure type[/red]")
    else:
        rows, cols = 1, 1
        print("[red]Error: unknown figure type[/red]")

    if debug:
        print("[cyan]Detected number of subplots: " + str(rows * cols) + "[/cyan]")

    if figsize == None:
        figsize = (800 + 400 * (cols - 1), 600 + 200 * (rows - 1))

    default_margin = {"color": "white", "margin": (0, 0, 0, 0)}
    if margin != None:
        for key in default_margin.keys():
            if key not in margin.keys():
                margin[key] = default_margin[key]

    fig.update_layout(
        title=title,
        legend=legend,
        template="presentation",
        font=dict(size=fontsize),
        paper_bgcolor=margin["color"],
        bargap=0,
    )  # font size and template

    fig.update_xaxes(
        matches=matches[0],
        showline=True,
        mirror="ticks",
        showgrid=True,
        minor_ticks="inside",
        tickformat=tickformat[0],
        # range=ranges[0],
    )  # tickformat=",.1s" for scientific notation

    if ranges[0] != None:
        fig.update_xaxes(range=ranges[0])
    if ranges[1] != None:
        fig.update_yaxes(range=ranges[1])

    fig.update_yaxes(
        matches=matches[1],
        showline=True,
        mirror="ticks",
        showgrid=True,
        minor_ticks="inside",
        tickformat=tickformat[1],
        # range=ranges[1],
    )  # tickformat=",.1s" for scientific notation

    if figsize != None:
        fig.update_layout(width=figsize[0], height=figsize[1])
    if log[0]:
        fig.update_xaxes(type="log", tickmode="linear")
    if log[1]:
        fig.update_yaxes(type="log", tickmode="linear")
    if margin["auto"] == False:
        fig.update_layout(
            margin=dict(
                l=margin["margin"][0],
                r=margin["margin"][1],
                t=margin["margin"][2],
                b=margin["margin"][3],
            )
        )
    # Update axis labels to include units
    if add_units:
        try:
            fig.update_xaxes(
                title_text=fig.layout.xaxis.title.text
                + get_run_units(fig.layout.xaxis.title.text, debug=debug)
            )
        except AttributeError:
            pass
        try:
            fig.update_yaxes(
                title_text=fig.layout.yaxis.title.text
                + get_run_units(fig.layout.yaxis.title.text, debug=debug)
            )
        except AttributeError:
            pass
    return fig


def get_run_units(var, debug=False):
    """Returns the units of a variable based on the variable name

    :param var: variable name
    :type var: str
    :param debug: True to print debug statements, False otherwise, defaults to False
    :type debug: bool
    
    :return: units
    :rtype: str
    """

    units = {
        "R": " (cm) ",
        "X": " (cm) ",
        "Y": " (cm) ",
        "Z": " (cm) ",
        "E": " (MeV) ",
        "P": " (MeV) ",
        "PE": " (counts) ",
        "Time": " (s) ",
        "Energy": " (MeV) ",
        "Charge": " (ADC x tick) ",
    }
    unit = ""
    for unit_key in list(units.keys()):
        if debug:
            print("Checking for " + unit_key + " in " + var)
        if var.endswith(unit_key):
            unit = units[unit_key]
            if debug:
                print("Unit found for " + var)
                
    return unit


def unicode(x):
    """Returns the unicode character for a given string

    :param x: string to convert to unicode
    :type x: str
    
    :return: unicode character
    :rtype: str
    """
    if type(x) != str:
        raise TypeError("Input must be a string")
    unicode_greek = {
        "Delta": "\u0394",
        "mu": "\u03BC",
        "pi": "\u03C0",
        "gamma": "\u03B3",
        "Sigma": "\u03A3",
        "Lambda": "\u039B",
        "alpha": "\u03B1",
        "beta": "\u03B2",
        "gamma": "\u03B3",
        "delta": "\u03B4",
        "epsilon": "\u03B5",
        "zeta": "\u03B6",
        "eta": "\u03B7",
        "theta": "\u03B8",
        "iota": "\u03B9",
        "kappa": "\u03BA",
        "lambda": "\u03BB",
        "mu": "\u03BC",
        "nu": "\u03BD",
        "xi": "\u03BE",
        "omicron": "\u03BF",
        "pi": "\u03C0",
        "rho": "\u03C1",
        "sigma": "\u03C3",
        "tau": "\u03C4",
        "upsilon": "\u03C5",
        "phi": "\u03C6",
        "chi": "\u03C7",
        "psi": "\u03C8",
        "omega": "\u03C9",
    }

    unicode_symbol = {
        "PlusMinus": "\u00B1",
        "MinusPlus": "\u2213",
        "Plus": "\u002B",
        "Minus": "\u2212",
        "Equal": "\u003D",
        "NotEqual": "\u2260",
        "LessEqual": "\u2264",
        "GreaterEqual": "\u2265",
        "Less": "\u003C",
        "Greater": "\u003E",
        "Approximately": "\u2248",
        "Proportional": "\u221D",
        "Infinity": "\u221E",
        "Degree": "\u00B0",
        "Prime": "\u2032",
        "DoublePrime": "\u2033",
        "TriplePrime": "\u2034",
        "QuadruplePrime": "\u2057",
        "Micro": "\u00B5",
        "PerMille": "\u2030",
        "Permyriad": "\u2031",
        "Minute": "\u2032",
        "Second": "\u2033",
        "Dot": "\u02D9",
        "Cross": "\u00D7",
        "Star": "\u22C6",
        "Circle": "\u25CB",
        "Square": "\u25A1",
        "Diamond": "\u25C7",
        "Triangle": "\u25B3",
        "LeftTriangle": "\u22B2",
        "RightTriangle": "\u22B3",
        "LeftTriangleEqual": "\u22B4",
        "RightTriangleEqual": "\u22B5",
        "LeftTriangleBar": "\u29CF",
        "RightTriangleBar": "\u29D0",
        "LeftTriangleEqualBar": "\u29CF",
        "RightTriangleEqualBar": "\u29D0",
        "LeftRightArrow": "\u2194",
        "UpDownArrow": "\u2195",
        "UpArrow": "\u2191",
        "DownArrow": "\u2193",
        "LeftArrow": "\u2190",
        "RightArrow": "\u2192",
        "UpArrowDownArrow": "\u21C5",
        "LeftArrowRightArrow": "\u21C4",
        "LeftArrowLeftArrow": "\u21C7",
        "UpArrowUpArrow": "\u21C8",
        "RightArrowRightArrow": "\u21C9",
        "DownArrowDownArrow": "\u21CA",
        "LeftRightVector": "\u294E",
        "RightUpDownVector": "\u294F",
        "DownLeftRightVector": "\u2950",
        "LeftUpDownVector": "\u2951",
        "LeftVectorBar": "\u2952",
        "RightVectorBar": "\u2953",
        "RightUpVectorBar": "\u2954",
        "RightDownVectorBar": "\u2955",
    }

    unicode_dict = {**unicode_greek, **unicode_symbol}
    
    return unicode_dict[x]
