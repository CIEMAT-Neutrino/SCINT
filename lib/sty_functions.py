import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("Qt5Agg")
import plotly.express as px

from rich import print as print

styles = ["CIEMAT_style"]
import importlib.util

try:
    importlib.util.find_spec("dunestyle.matplotlib")
    styles.append("DUNE_style")
except:
    pass
try:
    importlib.util.find_spec("mplhep")
    styles.append("HEP_style")
except:
    pass
from .io_functions import check_key
from .fig_config import figure_features, add_grid

for style in styles:
    print(
        f" \t * You can change your plotting style with [green]OPT[STYLE]={style}![/green]"
    )


def style_selector(OPT):
    if check_key(OPT, "STYLE") == False:
        OPT["STYLE"] = "CIEMAT_style"
    if OPT["STYLE"] == "None":
        pass
    if OPT["STYLE"] == "CIEMAT_style":
        figure_features()
    if OPT["STYLE"] == "DUNE_style":
        import dunestyle.matplotlib as dune
    if OPT["STYLE"] == "HEP_style":
        import mplhep as hep

        plt.rcParams.update({"font.size": 14})
        # Include watermark to the top left of the plot
        # plt.text(0.02, 0.98, "Preliminary", fontsize=14, color='gray', alpha=0.5, transform=plt.gca().transAxes, ha='left', va='top')

    if OPT["STYLE"] == "ATLAS_style":
        import mplhep as hep

        hep.style.use("ATLAS")
    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(color=get_prism_colors())


def get_prism_colors():
    prism = [c.split("rgb")[-1] for c in px.colors.qualitative.Prism]
    # Convert strng of tuple of int to tuple of int
    prism = [tuple(int(c) / 255 for c in s[1:-1].split(",")) for s in prism]
    # Change the order of the colors: insert the first color at the second to last position
    prism.insert(-1, prism.pop(0))
    # print(prism)
    return prism


def get_color(number, even=True, style="prism", debug=False):
    if style == "prism":
        colors = get_prism_colors()
    else:
        # Use standard matplotlib colors
        colors = [c for c in plt.rcParams["axes.prop_cycle"].by_key()["color"]]
    if even:
        number = get_even_color(number)
    else:
        number = 1 + get_even_color(number)
    return colors[number]


def get_even_color(number):
    try:
        number = int(number)
    except ValueError:
        number = int(number.split("+")[0])

    number = number - 2
    if number % 2 == 0:
        pass
    else:
        number = number - 1 if number > 0 else number + 1
    return number
