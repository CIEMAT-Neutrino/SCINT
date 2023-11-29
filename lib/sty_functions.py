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
    if OPT["STYLE"] == "CIEMAT_style": figure_features()
    if OPT["STYLE"] == "DUNE_style":   import dunestyle.matplotlib as dune
    if OPT["STYLE"] == "HEP_style":    import mplhep as hep