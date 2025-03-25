import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
}

user_input, info = initialize_macro(
    "0YVisHist1D",
    ["input_file", "runs", "channels", "variables", "filter", "group", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)
OPT = opt_selector(arguments=["STATS", "COMPARE", "NORM", "XLIM", "YLIM", "LOGX", "LOGY"], debug=user_input["debug"])

### 0YVisHist1D
my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    preset="EVA",
    info=info,
    compressed=True,
    debug=user_input["debug"],
)
if check_key(OPT, "PE") and OPT["PE"]:
    my_runs = calibrate_charges(my_runs, info, user_input, debug=user_input["debug"])
    for var_idx, var in enumerate(user_input["variables"]):
        user_input["variables"][var_idx] = var + "PE"

if user_input["group"]:
    my_runs = group_selector(my_runs)
    
label, my_runs = cut_selector(my_runs, user_input, debug=user_input["debug"])

vis_var_hist(
    my_runs,
    info,
    user_input["variables"],
    percentile=OPT["PERCENTILE"],
    OPT=OPT,
    select_range=False,
    save=user_input["save"],
    debug=user_input["debug"],
)
