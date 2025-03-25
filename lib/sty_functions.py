import matplotlib
import importlib.util
import plotly.express as px

from typing import Optional
from rich import print as rprint
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from .io_functions import check_key
from .fig_config import figure_features, add_grid

matplotlib.use("Qt5Agg")


def style_selector(OPT: Optional[dict] = None):
    if OPT is None:
        OPT = {}
        OPT["STYLE"] = "CIEMAT"
    
    elif isinstance(OPT, dict) == True and "STYLE" not in OPT.keys():
        OPT["STYLE"] = "CIEMAT"

    styles = ["CIEMAT"]
    if check_key(OPT, "STYLE") == False:
        pass
    
    if OPT["STYLE"] == "CIEMAT":
        figure_features()
    
    if OPT["STYLE"] == "DUNE":
        import dunestyle.matplotlib as dune
        try:
            importlib.util.find_spec("dune")
            styles.append("DUNE")
        
        except: 
            rprint("DUNE style not found")
    
    if OPT["STYLE"] == "HEP" or OPT["STYLE"] == "ATLAS":
        import mplhep as hep
        try:
            importlib.util.find_spec("hep")
            styles.append("HEP", "ATLAS")
        
        except:
            rprint("HEP style not found")
        
        if OPT["STYLE"] == "ATLAS":
            hep.style.use("ATLAS")
            # Include watermark to the top left of the plot
            # plt.text(0.02, 0.98, "Preliminary", fontsize=14, color='gray', alpha=0.5, transform=plt.gca().transAxes, ha='left', va='top')
        plt.rcParams.update({"font.size": 14})

    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(color=get_prism_colors())
    rprint(f"* You can change your plotting style with [green]OPT[STYLE]={styles}![/green]")


def get_prism_colors():
    prism = [c.split("rgb")[-1] for c in px.colors.qualitative.Prism]
    # Convert strng of tuple of int to tuple of int
    prism = [tuple(int(c) / 255 for c in s[1:-1].split(",")) for s in prism]
    # Change the order of the colors: insert the first color at the second to last position
    prism.insert(-1, prism.pop(0))
    # rprint(prism)
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
