
styles = ["CIEMAT_style"]
import importlib.util
if importlib.util.find_spec("dunestyle.matplotlib") is not None: styles.append("DUNE_style")
if importlib.util.find_spec("mplhep") is not None:               styles.append("HEP_style")
for style in styles: print(" \t * You can change your plotting style with "+ '\033[1m' + "OPT[STYLE]=" + style + '\033[0m' +" !")

#  Import from other libraries
from .io_functions  import check_key
def style_selector(OPT):
    if check_key(OPT,"STYLE") == False: OPT["STYLE"] = "CIEMAT_style"
    if OPT["STYLE"] == "CIEMAT_style": from lib.fig_config import (figure_features, add_grid); figure_features()
    if OPT["STYLE"] == "DUNE_style":   import dunestyle.matplotlib as dune
    if OPT["STYLE"] == "HEP_style":    import mplhep as hep