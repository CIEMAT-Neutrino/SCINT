import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px

from rich import print as print

styles = ["CIEMAT_style"]
import importlib.util
try: importlib.util.find_spec("dunestyle.matplotlib"); styles.append("DUNE_style")
except: pass
try: importlib.util.find_spec("mplhep"); styles.append("HEP_style")
except: pass

for style in styles: print(" \t * You can change your plotting style with "+ '\033[1m' + "OPT[STYLE]=" + style + '\033[0m' +" !")

#  Import from other libraries
from .io_functions import check_key
from .fig_config   import (figure_features, add_grid); 
def style_selector(OPT):
    if check_key(OPT,"STYLE") == False: OPT["STYLE"] = "CIEMAT_style"
    if OPT["STYLE"] == "None": pass
    if OPT["STYLE"] == "CIEMAT_style":
        figure_features()
        # mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=get_prism_colors()) 
    if OPT["STYLE"] == "DUNE_style":   import dunestyle.matplotlib as dune
    if OPT["STYLE"] == "HEP_style": import mplhep as hep
    if OPT["STYLE"] == "ATLAS_style":
        import mplhep as hep
        hep.style.use("ATLAS")
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=get_prism_colors()) 

def get_prism_colors():
    prism = [c.split("rgb")[-1] for c in px.colors.qualitative.Prism]
    # Convert strng of tuple of int to tuple of int
    prism = [tuple(int(c)/255 for c in s[1:-1].split(',')) for s in prism]
    # Change the order of the colors: insert the first color at the second to last position
    prism.insert(-1, prism.pop(0))
    # print(prism)
    return prism